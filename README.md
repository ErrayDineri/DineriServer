# Dineri Server

Dineri Server is a self-hosted media management platform that combines torrent searching, downloading, and media organizing capabilities in a single, elegant web interface.

[![✨ Try the demo](https://img.shields.io/badge/Demo-Click%20Here-blue?style=for-the-badge&logo=appveyor)](https://drive.google.com/file/d/1HzEkhbzGOm5P91hzmYkSb3yGAZu_9xaO/view?usp=sharing)

## 🌟 Features

### ✨ Recent Updates
- **Enhanced Password Manager**: CSV import functionality for easy migration from other password managers
- **Modern UI Overhaul**: Complete redesign with glassmorphism effects and smooth animations
- **Improved Navigation**: Consistent header styling and better visual hierarchy across all pages
- **Better Form Handling**: Enhanced form validation and user feedback systems

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
- Automatic media conversion to HLS format for compatibility
- Clean, modern UI for browsing your content
- Built-in video streaming with adaptive quality

### 🔐 Password Manager
- Secure password vault with master password protection
- Store and organize login credentials for various services
- AES encryption for secure password storage
- Easy-to-use interface for adding, editing, and managing passwords
- **CSV Import**: Import passwords from Bitwarden and other password managers
- Support for bulk password imports with duplicate detection
- Search and filter functionality for quick password retrieval
- Secure session management with automatic logout
- Modern glassmorphism UI with intuitive password management

### 👤 User Management
- User registration and authentication system
- Secure login with session management
- Individual user accounts and preferences
- Account creation and management interface

### 🎨 User Experience
- Modern, responsive dark/light theme with beautiful gradient backgrounds
- Glass-morphism card design for an elegant, premium look and feel
- Smooth animations and transitions throughout the interface
- Mobile-friendly responsive interface that works on all devices
- Modern UI components with hover effects and interactive elements
- Consistent design language across all application modules
- Enhanced form styling with modern input groups and validation
- Intuitive navigation with contextual actions and clear visual hierarchy

## 🛠️ Technical Details

### Built With
- **Backend**: Django (Python web framework)
- **Frontend**: Bootstrap 5, jQuery, Font Awesome, Custom CSS with animations
- **Database**: SQLite (default) with support for PostgreSQL/MySQL
- **Torrent Engine**: qBittorrent (via Web API)
- **Task Queue**: Celery with Redis for background processing
- **Security**: AES encryption for password storage, CSRF protection
- **Scrapers**: Custom web scrapers for multiple torrent sites

### Project Structure
- **apps/search**: Handles torrent searching across multiple sources
- **apps/torrents**: Manages torrent downloading and status tracking
- **apps/dashboard**: Provides the main dashboard interface with system overview
- **apps/mediahub**: Media organization, streaming, and browsing
- **apps/passwordmanager**: Secure password vault with CSV import and credential management
- **apps/accounts**: User authentication, registration, and account management

### Key Features by Module
- **Password Manager**: AES-256 encryption, CSV import/export, duplicate detection, secure master password system
- **Search Engine**: Multi-threaded scraping, result aggregation, smart filtering and sorting
- **Media Hub**: Automatic transcoding, HLS streaming, responsive video player
- **Dashboard**: Real-time system monitoring, elegant glassmorphism interface

### Requirements
- Python 3.8+
- qBittorrent with Web UI enabled (port 8090)
- Internet connection for scraping torrent sites
- FFmpeg for media conversion (installed on the host system)
- Redis for Celery task queue (can be run in Docker)

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd DineriServer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up external services**
   - Install and configure qBittorrent with Web UI enabled (port 8090)
   - Install FFmpeg and ensure it's available in your system PATH
   - Start Redis server: `docker run -p 6379:6379 -d redis:alpine`

4. **Initialize the database**
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

5. **Start background services**
   ```bash
   # Terminal 1: Start Celery worker
   celery -A homeserver worker --loglevel=info
   
   # Terminal 2: Start Celery beat scheduler
   celery -A homeserver beat --loglevel=info
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open your browser to http://localhost:8000
   - Create an account and start using the platform

## 📝 License

This project is for personal, non-commercial use only. The use of this software to download copyrighted material without permission is against the law.

## 🔗 Contact

Created by Rayen Guermazi - feel free to contact me!

---

⚠️ **Disclaimer**: This software is intended for downloading freely available content or content you have the rights to download. Users are responsible for adhering to their local laws regarding content downloading and sharing.
