# Spotify Downloader
Welcome to the Spotify Downloader, a powerful and user-friendly desktop application that allows you to download Spotify playlists as MP3 or WAV files. This tool is designed for music lovers who want to enjoy their favorite Spotify playlists offline, without needing a premium subscription.

# How It Works
The Spotify Downloader uses the Spotify API to fetch playlist data and yt-dlp to search and download the corresponding audio tracks from YouTube. The downloaded tracks are then converted into your preferred format (MP3 or WAV) using FFmpeg.

## Key Features:

Spotify Playlist Integration: Connect to Spotify using your API credentials and load any public playlist.

Audio Format Selection: Choose between MP3 or WAV formats for your downloads.

Encrypted Credential Storage: Your Spotify API credentials are securely encrypted and stored locally.

User-Friendly Interface: Built with PyQt5, the app provides a sleek and intuitive interface inspired by Spotify's design.

Executable File: The application is available as a standalone `Downloader.exe` file for easy use on Windows.

# Usage
Prerequisites
Before running the application, ensure you have the following:

Windows OS: The `Downloader.exe` file is designed for Windows.

FFmpeg: Ensure FFmpeg is installed and added to your system's PATH for audio conversion.

The only Installation needed is to run ```pip install -r requirements.txt```

## Steps to Use
### Download the Application:

Download the `Downloader.exe` file from the repository or release section.

### Run the Application:

Double-click the `Downloader.exe` file to launch the application.

### Connect to Spotify:

Enter your Spotify API `Client ID` and `Client` Secret in the respective fields.

Click Connect to authenticate with Spotify.

### Load a Playlist:

Paste the URL of the Spotify playlist you want to download.

Click Load Playlist to fetch the list of songs.

### Choose Audio Format:

Select either MP3 or WAV as your preferred format.

### Download Songs:

Click Download and select the folder where you want to save the audio files.

The application will search for each song on YouTube, download the audio, and convert it to your chosen format.

### Logout:

If you want to clear your credentials, click Logout.

# Important Notes
### Spotify API Credentials: 
To use this application, you need to create a Spotify Developer account and register an app to obtain your `Client ID` and `Client Secret`. Follow the [Spotify Developer Guide](https://developer.spotify.com/documentation/web-api/concepts/apps) for detailed instructions.

### Legal Disclaimer: 
Downloading copyrighted material without proper authorization may violate Spotify's terms of service and copyright laws. Use this tool responsibly and only for playlists you own or have permission to download.

### YouTube Dependency: 
The application relies on YouTube as the source for audio downloads. Ensure you have a stable internet connection for smooth operation.

### FFmpeg Requirement: 
FFmpeg is required for audio conversion. If you don't have it installed, download it from [Here](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip) and add it to your system's PATH.

# Contributing
Contributions are welcome! If you'd like to improve this project, please follow these steps:

Fork the repository.

Create a new branch for your feature or bugfix.

Commit your changes and push to the branch.

Submit a pull request with a detailed description of your changes.

# Support
If you encounter any issues or have questions, feel free to open an issue on the GitHub repository.
