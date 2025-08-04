import sys
import os
import re
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QRadioButton, QFileDialog, QStackedWidget,
                            QListWidget, QListWidgetItem, QCheckBox, QComboBox,
                            QProgressBar, QFrame, QScrollArea, QGridLayout,
                            QMessageBox, QSpacerItem, QSizePolicy, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor

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

class PlaylistLoader(QThread):
    progress = pyqtSignal(str)
    playlist_loaded = pyqtSignal(list, str)
    error = pyqtSignal(str)

    def __init__(self, sp, playlist_url):
        super().__init__()
        self.sp = sp
        self.playlist_url = playlist_url

    def run(self):
        try:
            self.progress.emit("Extracting playlist ID...")
            self.msleep(100)  

            match = re.search(r"playlist/([\w\d]+)", self.playlist_url)
            if not match:
                self.error.emit("Invalid playlist URL. Please enter a valid Spotify playlist URL.")
                return

            playlist_id = match.group(1)
            self.progress.emit("Loading playlist information...")
            self.msleep(100)  

            playlist_info = self.sp.playlist(playlist_id)

            self.progress.emit("Fetching tracks...")
            self.msleep(100)  

            tracks = []
            offset = 0
            limit = 100

            while True:
                results = self.sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
                for track_item in results['items']:
                    track = track_item['track']
                    if track:
                        name = track['name']
                        artist = track['artists'][0]['name']
                        tracks.append(f"{name} - {artist}")

                if len(results['items']) < limit:
                    break
                offset += limit

                if offset % 100 == 0:
                    self.msleep(50)

            self.playlist_loaded.emit(tracks, playlist_info['name'])

        except Exception as e:
            self.error.emit(f"Failed to load playlist: {str(e)}")

class DownloadWorker(QThread):
    progress = pyqtSignal(str)
    song_progress = pyqtSignal(str, int)
    download_complete = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, songs, output_folder, format_choice, quality):
        super().__init__()
        self.songs = songs
        self.output_folder = output_folder
        self.format_choice = format_choice
        self.quality = quality
        self.is_running = True

    def run(self):
        try:
            for i, song in enumerate(self.songs):
                if not self.is_running:
                    break

                self.progress.emit(f"Downloading: {song}")
                self.song_progress.emit(song, int((i / len(self.songs)) * 100))

                query = f"ytsearch:{song.strip()} audio"
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': f'{self.output_folder}/%(title)s.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': self.format_choice,
                        'preferredquality': self.quality,
                    }],
                    'quiet': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([query])

            self.download_complete.emit()
        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        self.is_running = False

class LoginScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("Spotify Downloader")
        title.setFont(QFont("Helvetica", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1DB954; margin-bottom: 20px;")
        layout.addWidget(title)

        subtitle = QLabel("Download your favorite playlists")
        subtitle.setFont(QFont("Helvetica", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #B3B3B3; margin-bottom: 30px;")
        layout.addWidget(subtitle)

        credentials_group = QGroupBox("Spotify API Credentials")
        credentials_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: 
                border: 2px solid 
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        credentials_layout = QVBoxLayout(credentials_group)
        credentials_layout.setSpacing(15)

        self.client_id = QLineEdit()
        self.client_id.setPlaceholderText("Client ID")
        self.client_id.setStyleSheet("""
            QLineEdit {
                background-color: 
                color: 
                border: 2px solid 
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid 
            }
        """)
        credentials_layout.addWidget(self.client_id)

        self.client_secret = QLineEdit()
        self.client_secret.setPlaceholderText("Client Secret")
        self.client_secret.setEchoMode(QLineEdit.Password)
        self.client_secret.setStyleSheet("""
            QLineEdit {
                background-color: 
                color: 
                border: 2px solid 
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid 
            }
        """)
        credentials_layout.addWidget(self.client_secret)

        layout.addWidget(credentials_group)

        button_layout = QHBoxLayout()

        self.login_btn = QPushButton("Login")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: 
                color: 
                border: none;
                border-radius: 25px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: 
            }
            QPushButton:pressed {
                background-color: 
            }
        """)
        self.login_btn.clicked.connect(self.login)
        button_layout.addWidget(self.login_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: 
                color: 
                border: none;
                border-radius: 25px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: 
            }
        """)
        self.clear_btn.clicked.connect(self.clear_credentials)
        button_layout.addWidget(self.clear_btn)

        layout.addLayout(button_layout)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #B3B3B3; margin-top: 10px;")
        layout.addWidget(self.status_label)

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
            except Exception as e:
                self.status_label.setText(f"Error loading credentials: {str(e)}")

    def save_credentials(self):
        try:
            encrypted_id = encrypt_credentials(self.client_id.text())
            encrypted_secret = encrypt_credentials(self.client_secret.text())
            with open("credential.cdi", "w", encoding="utf-8") as file:
                file.write(f"{encrypted_id}\n{encrypted_secret}")
        except Exception as e:
            self.status_label.setText(f"Error saving credentials: {str(e)}")

    def login(self):
        if not self.client_id.text() or not self.client_secret.text():
            self.status_label.setText("Please enter both Client ID and Client Secret")
            return

        try:
            self.parent.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                client_id=self.client_id.text(),
                client_secret=self.client_secret.text()
            ))
            self.save_credentials()
            self.status_label.setText("Login successful!")
            QTimer.singleShot(1000, self.parent.show_main_screen)
        except Exception as e:
            self.status_label.setText(f"Login failed: {str(e)}")

    def clear_credentials(self):
        self.client_id.clear()
        self.client_secret.clear()
        if os.path.exists("credential.cdi"):
            os.remove("credential.cdi")
        self.status_label.setText("Credentials cleared")

class MainScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.selected_playlist = None
        self.songs = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        header_layout = QHBoxLayout()

        title = QLabel("Spotify Playlist Downloader")
        title.setFont(QFont("Helvetica", 20, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: 
                color: 
                border: none;
                border-radius: 20px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: 
            }
        """)
        self.logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_btn)

        layout.addLayout(header_layout)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background-color: 
                border: 2px solid 
                border-radius: 8px;
            }
        """)
        left_layout = QVBoxLayout(left_panel)

        playlist_label = QLabel("Playlist Input")
        playlist_label.setFont(QFont("Helvetica", 14, QFont.Bold))
        playlist_label.setStyleSheet("color: #FFFFFF; padding: 10px;")
        left_layout.addWidget(playlist_label)

        playlist_url_label = QLabel("Playlist URL")
        playlist_url_label.setFont(QFont("Helvetica", 12, QFont.Bold))
        playlist_url_label.setStyleSheet("color: #FFFFFF; padding: 10px 0;")
        left_layout.addWidget(playlist_url_label)

        self.playlist_url = QLineEdit()
        self.playlist_url.setPlaceholderText("Paste Spotify playlist URL here...")
        self.playlist_url.setStyleSheet("""
            QLineEdit {
                background-color: 
                color: 
                border: 2px solid 
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid 
            }
        """)
        left_layout.addWidget(self.playlist_url)

        self.load_playlist_btn = QPushButton("Load Playlist")
        self.load_playlist_btn.setStyleSheet("""
            QPushButton {
                background-color: 
                color: 
                border: none;
                border-radius: 20px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: 
            }
        """)
        self.load_playlist_btn.clicked.connect(self.load_playlist_songs)
        left_layout.addWidget(self.load_playlist_btn)

        left_layout.addStretch()

        content_layout.addWidget(left_panel, 1)

        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: 
                border: 2px solid 
                border-radius: 8px;
            }
        """)
        right_layout = QVBoxLayout(right_panel)

        settings_group = QGroupBox("Download Settings")
        settings_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: 
                border: 2px solid 
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        settings_layout = QGridLayout(settings_group)

        format_label = QLabel("Format:")
        format_label.setStyleSheet("color: #B3B3B3;")
        settings_layout.addWidget(format_label, 0, 0)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP3", "WAV", "FLAC", "AAC"])
        self.format_combo.setStyleSheet("""
            QComboBox {
                background-color: 
                color: 
                border: 1px solid 
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid 
            }
        """)
        settings_layout.addWidget(self.format_combo, 0, 1)

        quality_label = QLabel("Quality:")
        quality_label.setStyleSheet("color: #B3B3B3;")
        settings_layout.addWidget(quality_label, 1, 0)

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["128k", "192k", "256k", "320k"])
        self.quality_combo.setCurrentText("192k")
        self.quality_combo.setStyleSheet("""
            QComboBox {
                background-color: 
                color: 
                border: 1px solid 
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid 
            }
        """)
        settings_layout.addWidget(self.quality_combo, 1, 1)

        right_layout.addWidget(settings_group)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #B3B3B3; padding: 5px;")
        right_layout.addWidget(self.status_label)

        songs_label = QLabel("Songs")
        songs_label.setFont(QFont("Helvetica", 14, QFont.Bold))
        songs_label.setStyleSheet("color: #FFFFFF; padding: 10px 0;")
        right_layout.addWidget(songs_label)

        select_layout = QHBoxLayout()

        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: 
                color: 
                border: none;
                border-radius: 15px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: 
            }
        """)
        self.select_all_btn.clicked.connect(self.select_all_songs)
        select_layout.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton("Deselect All")
        self.deselect_all_btn.setStyleSheet("""
            QPushButton {
                background-color: 
                color: 
                border: none;
                border-radius: 15px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: 
            }
        """)
        self.deselect_all_btn.clicked.connect(self.deselect_all_songs)
        select_layout.addWidget(self.deselect_all_btn)

        select_layout.addStretch()
        right_layout.addLayout(select_layout)

        self.songs_list = QListWidget()
        self.songs_list.setMinimumHeight(300)  
        self.songs_list.setStyleSheet("""
            QListWidget {
                background-color: 
                color: 
                border: 1px solid 
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid 
                min-height: 50px;
                margin: 2px 0px;
            }
            QListWidget::item:hover {
                background-color: 
            }
        """)
        right_layout.addWidget(self.songs_list)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid 
                border-radius: 5px;
                text-align: center;
                background-color: 
            }
            QProgressBar::chunk {
                background-color: 
                border-radius: 3px;
            }
        """)
        right_layout.addWidget(self.progress_bar)

        self.download_btn = QPushButton("Download Selected Songs")
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: 
                color: 
                border: none;
                border-radius: 25px;
                padding: 12px 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: 
            }
            QPushButton:disabled {
                background-color: 
            }
        """)
        self.download_btn.clicked.connect(self.download_songs)
        self.download_btn.setEnabled(False)
        right_layout.addWidget(self.download_btn)

        content_layout.addWidget(right_panel, 2)
        layout.addLayout(content_layout)

    def load_playlist_songs(self):
        if not self.parent.sp:
            QMessageBox.warning(self, "Error", "Please login to Spotify first.")
            return

        playlist_url = self.playlist_url.text().strip()
        if not playlist_url:
            QMessageBox.warning(self, "Error", "Please enter a playlist URL.")
            return

        self.load_playlist_btn.setEnabled(False)
        self.load_playlist_btn.setText("Loading...")
        self.status_label.setText("Loading playlist...")
        self.songs_list.clear()

        self.playlist_loader = PlaylistLoader(self.parent.sp, playlist_url)
        self.playlist_loader.progress.connect(self.update_loading_status)
        self.playlist_loader.playlist_loaded.connect(self.on_playlist_loaded)
        self.playlist_loader.error.connect(self.on_playlist_error)
        self.playlist_loader.finished.connect(self.on_playlist_finished)
        self.playlist_loader.start()

    def update_loading_status(self, message):
        self.status_label.setText(message)

    def on_playlist_loaded(self, tracks, playlist_name):
        print(f"Playlist loaded: {len(tracks)} tracks")  
        print(f"First few tracks: {tracks[:3] if tracks else 'No tracks'}")  

        QTimer.singleShot(0, lambda: self._update_ui_with_songs(tracks, playlist_name))

    def _update_ui_with_songs(self, tracks, playlist_name):
        print("Updating UI in main thread")  
        self.songs = tracks
        self.update_songs_list()
        self.download_btn.setEnabled(True)

        self.load_playlist_btn.setEnabled(True)
        self.load_playlist_btn.setText("Load Playlist")
        self.status_label.setText(f"Loaded {len(tracks)} songs from '{playlist_name}'")

        QMessageBox.information(self, "Success", f"Loaded {len(tracks)} songs from '{playlist_name}'")

    def on_playlist_error(self, error):
        print(f"Playlist error: {error}")  

        QTimer.singleShot(0, lambda: self._update_ui_on_error(error))

    def _update_ui_on_error(self, error):

        self.load_playlist_btn.setEnabled(True)
        self.load_playlist_btn.setText("Load Playlist")
        self.status_label.setText("")

        QMessageBox.warning(self, "Error", error)

    def on_playlist_finished(self):
        print("Playlist loader thread finished")  

    def update_songs_list(self):
        print(f"Updating songs list with {len(self.songs)} songs")  
        self.songs_list.clear()

        if not self.songs:
            print("No songs to display")
            return

        for i, song in enumerate(self.songs):
            print(f"Adding song {i+1}: {song}")  

            item = QListWidgetItem()
            self.songs_list.addItem(item)

            widget = QWidget()
            layout = QHBoxLayout(widget)

            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: 
                    font-size: 14px;
                    font-weight: bold;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                }
                QCheckBox::indicator:checked {
                    background-color: 
                    border: 2px solid 
                    border-radius: 4px;
                }
                QCheckBox::indicator:unchecked {
                    background-color: 
                    border: 2px solid 
                    border-radius: 4px;
                }
            """)

            label = QLabel(song)
            label.setStyleSheet("""
                color: 
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            """)

            layout.addWidget(checkbox)
            layout.addWidget(label)
            layout.addStretch()
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(15)

            self.songs_list.setItemWidget(item, widget)

        print(f"Songs list updated. Total items: {self.songs_list.count()}")  

        self.songs_list.update()
        self.songs_list.repaint()

    def select_all_songs(self):
        for i in range(self.songs_list.count()):
            item = self.songs_list.item(i)
            widget = self.songs_list.itemWidget(item)
            checkbox = widget.findChild(QCheckBox)
            checkbox.setChecked(True)

    def deselect_all_songs(self):
        for i in range(self.songs_list.count()):
            item = self.songs_list.item(i)
            widget = self.songs_list.itemWidget(item)
            checkbox = widget.findChild(QCheckBox)
            checkbox.setChecked(False)

    def get_selected_songs(self):
        selected_songs = []
        for i in range(self.songs_list.count()):
            item = self.songs_list.item(i)
            widget = self.songs_list.itemWidget(item)
            checkbox = widget.findChild(QCheckBox)
            if checkbox.isChecked():
                label = widget.findChild(QLabel)
                selected_songs.append(label.text())
        return selected_songs

    def download_songs(self):
        selected_songs = self.get_selected_songs()
        if not selected_songs:
            QMessageBox.warning(self, "Warning", "Please select at least one song to download.")
            return

        output_folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if not output_folder:
            return

        format_choice = self.format_combo.currentText().lower()
        quality = self.quality_combo.currentText()

        self.download_worker = DownloadWorker(selected_songs, output_folder, format_choice, quality)
        self.download_worker.progress.connect(self.update_progress)
        self.download_worker.song_progress.connect(self.update_song_progress)
        self.download_worker.download_complete.connect(self.download_finished)
        self.download_worker.error.connect(self.download_error)

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.download_btn.setEnabled(False)
        self.download_worker.start()

    def update_progress(self, message):

        pass

    def update_song_progress(self, song, progress):
        self.progress_bar.setValue(progress)

    def download_finished(self):
        self.progress_bar.setVisible(False)
        self.download_btn.setEnabled(True)
        QMessageBox.information(self, "Success", "Download completed successfully!")

    def download_error(self, error):
        self.progress_bar.setVisible(False)
        self.download_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Download failed: {error}")

    def logout(self):
        if os.path.exists("credential.cdi"):
            os.remove("credential.cdi")
        self.parent.sp = None
        self.parent.show_login_screen()

class SpotifyDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Downloader")
        self.setGeometry(100, 100, 1200, 800)
        self.sp = None
        self.init_ui()

    def init_ui(self):

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.login_screen = LoginScreen(self)
        self.main_screen = MainScreen(self)

        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.main_screen)

        self.setStyleSheet("""
            QMainWindow {
                background-color: 
            }
        """)

        self.show_login_screen()

    def show_login_screen(self):
        self.stacked_widget.setCurrentWidget(self.login_screen)

    def show_main_screen(self):
        self.stacked_widget.setCurrentWidget(self.main_screen)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Helvetica", 10))
    window = SpotifyDownloader()
    window.show()
    sys.exit(app.exec_())