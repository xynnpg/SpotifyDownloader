# Spotify Downloader v2.0
Welcome to the enhanced Spotify Downloader, a powerful and user-friendly desktop application that allows you to download Spotify playlists as high-quality audio files. This tool is designed for music lovers who want to enjoy their favorite Spotify playlists offline.

## 🎵 New Features in v2.0

### ✨ Enhanced User Interface
- **Modern Login Screen**: Clean, Spotify-inspired login interface
- **Two-Screen Design**: Separate login and main application screens
- **Dark Theme**: Beautiful dark UI matching Spotify's design language
- **Responsive Layout**: Better organized interface with proper spacing

### 🔐 Secure Authentication
- **Encrypted Credential Storage**: Your Spotify API credentials are securely encrypted
- **Auto-Login**: Remembers your credentials for quick access
- **Secure Logout**: Properly clears stored credentials

### 📋 Playlist Management
- **URL Input**: Paste any Spotify playlist URL to load its songs
- **Universal Access**: Works with any public Spotify playlist
- **Quick Loading**: Instant playlist loading with track count display

### 🎛️ Quality & Format Control
- **Multiple Formats**: Choose from MP3, WAV, FLAC, or AAC
- **Quality Settings**: Select from 128k, 192k, 256k, or 320k bitrates
- **Real-time Preview**: See your format and quality selections

### 🎵 Smart Song Selection
- **Individual Checkboxes**: Select/deselect individual songs
- **Bulk Selection**: "Select All" and "Deselect All" buttons
- **Visual Feedback**: Clear indication of selected songs
- **Flexible Downloading**: Download only the songs you want

### ⚡ Enhanced Download Experience
- **Progress Tracking**: Real-time download progress bar
- **Background Processing**: Downloads run in background threads
- **Error Handling**: Graceful error handling with user-friendly messages
- **Download Status**: Clear feedback on download completion

## 🚀 How It Works
The Spotify Downloader uses the Spotify API to fetch your playlists and yt-dlp to search and download the corresponding audio tracks from YouTube. The downloaded tracks are then converted into your preferred format using FFmpeg.

## 📋 Prerequisites
Before running the application, ensure you have:

- **Python 3.7+**: Required for running the application
- **FFmpeg**: For audio conversion (download from [FFmpeg releases](https://github.com/BtbN/FFmpeg-Builds/releases))
- **Spotify API Credentials**: Client ID and Client Secret from Spotify Developer Dashboard

## 🛠️ Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Install FFmpeg** and add it to your system PATH
4. **Get Spotify API credentials** from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

## 🎯 Usage Guide

### Step 1: Login
1. Launch the application
2. Enter your Spotify API Client ID and Client Secret
3. Click "Login" to authenticate
4. Your credentials will be securely saved for future use

### Step 2: Load Playlist
1. Copy a Spotify playlist URL (from Spotify app or web)
2. Paste the URL in the left panel
3. Click "Load Playlist" to fetch the songs
4. The song list will appear in the right panel

### Step 3: Configure Settings
1. Choose your preferred audio format (MP3, WAV, FLAC, AAC)
2. Select audio quality (128k to 320k)
3. Use "Select All" or "Deselect All" to manage song selection
4. Check/uncheck individual songs as needed

### Step 4: Download
1. Click "Download Selected Songs"
2. Choose your download folder
3. Monitor progress with the progress bar
4. Enjoy your downloaded music!

## 🔧 Configuration

### Audio Formats
- **MP3**: Most compatible, good compression
- **WAV**: Uncompressed, highest quality
- **FLAC**: Lossless compression, high quality
- **AAC**: Good compression, high quality

### Quality Settings
- **128k**: Smaller file size, lower quality
- **192k**: Balanced quality and size (recommended)
- **256k**: High quality, larger files
- **320k**: Maximum quality, largest files

## 🔒 Security & Privacy
- **Local Storage**: All credentials stored locally on your device
- **Encryption**: Credentials are encrypted using XOR encryption
- **No Cloud Storage**: Your data never leaves your device
- **Secure Logout**: Complete credential removal on logout

## ⚠️ Important Notes

### Legal Disclaimer
Downloading copyrighted material without proper authorization may violate Spotify's terms of service and copyright laws. Use this tool responsibly and only for playlists you own or have permission to download.

### Spotify API Requirements
- Create a Spotify Developer account at [developer.spotify.com](https://developer.spotify.com)
- Register a new application to get Client ID and Client Secret
- No additional permissions required (uses public API)

### System Requirements
- **Windows**: Tested on Windows 10/11
- **Linux**: Tested on Arch Linux
- **macOS**: Should work with PyQt5 support
- **Internet**: Required for Spotify API and YouTube downloads

## 🐛 Troubleshooting

### Common Issues
1. **"Login failed"**: Check your Client ID and Client Secret
2. **"FFmpeg not found"**: Ensure FFmpeg is installed and in PATH
3. **"No playlists found"**: Verify your Spotify account has playlists
4. **"Download failed"**: Check internet connection and try again

### Getting Help
- Check that all dependencies are installed correctly
- Ensure FFmpeg is properly installed and accessible
- Verify your Spotify API credentials are correct
- Check your internet connection

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License
This project is for educational purposes. Please respect copyright laws and Spotify's terms of service.

## 🆘 Support
If you encounter any issues or have questions, please open an issue on the GitHub repository.

---

**Enjoy your music! 🎵**
