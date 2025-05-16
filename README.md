# Dineri Server

Dineri Server is a self-hosted media management platform that combines torrent searching, downloading, and media organizing capabilities in a single, elegant web interface.

## 🌟 Features

### 🔍 Multi-Source Torrent Search
- Search across multiple torrent sites simultaneously:
  - Nyaa
  - The Pirate Bay
  - 1337x
- Filter searches by specific sources or search all at once
- Sort results by seeders, leechers, size, or name

### 📥 Torrent Management
- Download torrents directly from the search interface
- Monitor download progress, speed, and status
- Manage torrents: pause, resume, force start, or delete
- View detailed torrent information including seeds, peers, and ETA

### 🎬 Media Organization
- Automatically stores downloaded content in an organized media library
- Supports video files and other media types
- Clean, modern UI for browsing your content

### 🎨 User Experience
- Modern, responsive dark theme with a beautiful gradient background
- Glass-like card design for an elegant look and feel
- Mobile-friendly interface

## 🛠️ Technical Details

### Built With
- **Backend**: Django (Python web framework)
- **Frontend**: Bootstrap 5, jQuery, Font Awesome
- **Torrent Engine**: qBittorrent (via API)
- **Scrapers**: Custom scrapers for multiple torrent sites

### Project Structure
- **apps/search**: Handles torrent searching across multiple sources
- **apps/torrents**: Manages torrent downloading and status tracking
- **apps/dashboard**: Provides the main dashboard interface
- **apps/mediahub**: Media organization and browsing

### Requirements
- Python 3.8+
- qBittorrent with Web UI enabled (port 8090)
- Internet connection for scraping torrent sites

## 🚀 Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Make sure qBittorrent is installed and configured
4. Run the server: `python manage.py runserver`
5. Open your browser to http://localhost:8000

## 📝 License

This project is for personal, non-commercial use only. The use of this software to download copyrighted material without permission is against the law.

## 🔗 Contact

Created by Rayen Guermazi - feel free to contact me!

---

⚠️ **Disclaimer**: This software is intended for downloading freely available content or content you have the rights to download. Users are responsible for adhering to their local laws regarding content downloading and sharing.
