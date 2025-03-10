import sys
import os
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QRadioButton, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Simple XOR encryption key
ENCRYPTION_KEY = b"SpotifyDownloader2025"

def encrypt_credentials(text):
    text_bytes = text.encode('utf-8')
    key_bytes = ENCRYPTION_KEY * (len(text_bytes) // len(ENCRYPTION_KEY) + 1)
    encrypted = bytes(a ^ b for a, b in zip(text_bytes, key_bytes[:len(text_bytes)]))
    return encrypted.hex()

def decrypt_credentials(encrypted_hex):
    encrypted_bytes = bytes.fromhex(encrypted_hex)
    key_bytes = ENCRYPTION_KEY * (len(encrypted_bytes) // len(ENCRYPTION_KEY) + 1)
    decrypted = bytes(a ^ b for a, b in zip(encrypted_bytes, key_bytes[:len(encrypted_bytes)]))
    return decrypted.decode('utf-8')

class SpotifyDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Downloader")
        self.setGeometry(100, 100, 500, 600)
        self.sp = None
        self.init_ui()

    def init_ui(self):
        # Spotify-inspired style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #181818;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Circular', 'Helvetica', sans-serif;
            }
            QLineEdit {
                background-color: #121212;
                color: #FFFFFF;
                border: 1px solid #3D3D3D;
                border-radius: 4px;
                padding: 8px;
            }
            QLineEdit:focus {
                border: 1px solid #1DB954;
            }
            QPushButton {
                background-color: #1DB954;
                color: #FFFFFF;
                border: none;
                border-radius: 20px;
                padding: 8px 16px;
                font-family: 'Circular', 'Helvetica', sans-serif;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1ED760;
            }
            QTextEdit {
                background-color: #121212;
                color: #B3B3B3;
                border: 1px solid #3D3D3D;
                border-radius: 4px;
                padding: 5px;
            }
            QRadioButton {
                color: #B3B3B3;
            }
            QRadioButton::indicator:checked {
                background-color: #1DB954;
            }
        """)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Spotify Downloader")
        title.setFont(QFont("Helvetica", 18, QFont.Bold))
        layout.addWidget(title)

        # Credentials
        self.client_id = QLineEdit()
        self.client_id.setPlaceholderText("Client ID")
        layout.addWidget(self.client_id)

        self.client_secret = QLineEdit()
        self.client_secret.setPlaceholderText("Client Secret")
        self.client_secret.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.client_secret)

        # Connect/Logout Buttons
        auth_layout = QHBoxLayout()
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect_spotify)
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        auth_layout.addWidget(connect_btn)
        auth_layout.addWidget(logout_btn)
        layout.addLayout(auth_layout)

        # Playlist
        self.playlist_url = QLineEdit()
        self.playlist_url.setPlaceholderText("Playlist URL")
        layout.addWidget(self.playlist_url)

        load_btn = QPushButton("Load Playlist")
        load_btn.clicked.connect(self.load_playlist)
        layout.addWidget(load_btn)

        # Format Selection
        format_layout = QHBoxLayout()
        self.mp3_radio = QRadioButton("MP3")
        self.mp3_radio.setChecked(True)
        self.wav_radio = QRadioButton("WAV")
        format_layout.addWidget(self.mp3_radio)
        format_layout.addWidget(self.wav_radio)
        format_layout.addStretch()
        layout.addLayout(format_layout)

        # Songs Display
        self.songs_display = QTextEdit()
        self.songs_display.setReadOnly(True)
        layout.addWidget(self.songs_display)

        # Download/Clear Buttons
        btn_layout = QHBoxLayout()
        download_btn = QPushButton("Download")
        download_btn.clicked.connect(self.download_songs)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_songs)
        btn_layout.addWidget(download_btn)
        btn_layout.addWidget(clear_btn)
        layout.addLayout(btn_layout)

        layout.addStretch()
        self.load_credentials()

    def load_credentials(self):
        if os.path.exists("credential.cdi"):
            try:
                with open("credential.cdi", "r", encoding="utf-8") as file:
                    lines = file.readlines()
                    if len(lines) >= 2:
                        client_id = decrypt_credentials(lines[0].strip())
                        client_secret = decrypt_credentials(lines[1].strip())
                        self.client_id.setText(client_id)
                        self.client_secret.setText(client_secret)
                        self.connect_spotify()
            except Exception as e:
                self.songs_display.setText(f"Error loading credentials: {str(e)}")

    def save_credentials(self):
        try:
            encrypted_id = encrypt_credentials(self.client_id.text())
            encrypted_secret = encrypt_credentials(self.client_secret.text())
            with open("credential.cdi", "w", encoding="utf-8") as file:
                file.write(f"{encrypted_id}\n{encrypted_secret}")
        except Exception as e:
            self.songs_display.setText(f"Error saving credentials: {str(e)}")

    def connect_spotify(self):
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                client_id=self.client_id.text(),
                client_secret=self.client_secret.text()
            ))
            self.save_credentials()
            self.songs_display.setText("Connected to Spotify.")
        except Exception as e:
            self.songs_display.setText(f"Connection failed: {str(e)}")

    def logout(self):
        if os.path.exists("credential.cdi"):
            os.remove("credential.cdi")
        self.client_id.clear()
        self.client_secret.clear()
        self.sp = None
        self.songs_display.setText("Logged out successfully.")

    def load_playlist(self):
        if not self.sp:
            self.songs_display.setText("Please connect to Spotify first.")
            return

        playlist_url = self.playlist_url.text()
        match = re.search(r"playlist/([\w\d]+)", playlist_url)
        if not match:
            self.songs_display.setText("Invalid playlist URL.")
            return

        try:
            playlist_id = match.group(1)
            playlist_info = self.sp.playlist(playlist_id)
            tracks = []
            offset = 0
            limit = 100

            while True:
                results = self.sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
                for item in results['items']:
                    track = item['track']
                    name = track['name']
                    artist = track['artists'][0]['name']
                    tracks.append(f"{name} - {artist}")

                if len(results['items']) < limit:
                    break
                offset += limit

            self.songs_display.setText("\n".join(tracks))
            self.songs_display.append(f"\nLoaded {len(tracks)} songs from '{playlist_info['name']}'")
        except Exception as e:
            self.songs_display.setText(f"Failed to load playlist: {str(e)}")

    def download_songs(self):
        if not self.songs_display.toPlainText().strip():
            self.songs_display.setText("No songs to download. Load a playlist first.")
            return

        format_choice = "mp3" if self.mp3_radio.isChecked() else "wav"
        output_folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if not output_folder:
            return

        os.makedirs(output_folder, exist_ok=True)
        songs = self.songs_display.toPlainText().strip().split("\n")

        try:
            for song in songs:
                if " - " not in song:  # Skip status messages
                    continue
                query = f"ytsearch:{song.strip()} audio"
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': format_choice,
                        'preferredquality': '192',
                    }],
                    'quiet': False,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([query])
            
            self.songs_display.append(f"\nDownloaded to {output_folder}")
        except Exception as e:
            self.songs_display.setText(f"Download failed: {str(e)}")

    def clear_songs(self):
        self.songs_display.clear()
        self.playlist_url.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Helvetica", 10))  # Spotify uses Circular, but Helvetica is close
    window = SpotifyDownloader()
    window.show()
    sys.exit(app.exec_())