# 🚀 Dineri Server

**A sophisticated, self-hosted media management and home server platform** that combines torrent searching, downloading, media organization, password management, and real-time system monitoring in a single, elegant web interface.

[![✨ Try the demo](https://img.shields.io/badge/Demo-Click%20Here-blue?style=for-the-badge&logo=appveyor)](https://drive.google.com/file/d/1HzEkhbzGOm5P91hzmYkSb3yGAZu_9xaO/view?usp=sharing)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2+-green?style=flat-square&logo=django)](https://djangoproject.com)
[![License](https://img.shields.io/badge/License-Personal%20Use-red?style=flat-square)](#-license)

## 🌟 Features Overview

Dineri Server is designed as a comprehensive home server solution that brings together multiple essential services in one beautiful, modern interface. Whether you're managing media, passwords, or monitoring your system, everything is accessible through an intuitive web dashboard.

### 🔍 **Multi-Source Torrent Search & Management**
- **Advanced Search Engine**: Search across multiple torrent sites simultaneously
  - **Supported Sources**: Nyaa, The Pirate Bay, 1337x
  - **Smart Filtering**: Filter by source, sort by seeders, size, or name
  - **Real-time Results**: Live search with instant result aggregation
- **Integrated Download Management**: 
  - Download torrents directly from search results
  - Real-time progress monitoring with speed and ETA
  - Full torrent control: pause, resume, force start, delete
  - Detailed statistics and peer information

### 🎬 **Media Hub & Streaming**
- **Automatic Media Organization**: Downloaded content is automatically organized
- **Built-in Streaming Server**: 
  - HLS adaptive streaming for optimal playback
  - Cross-platform video player with quality selection
  - Automatic media transcoding with FFmpeg
- **Modern Media Browser**: 
  - Beautiful grid layout with thumbnails
  - Search and filter your media collection
  - Responsive design for all devices

### 🔐 **Advanced Password Vault**
- **Military-Grade Security**: 
  - AES-256 encryption with user-specific salt
  - Master password protection with Argon2 key derivation
  - Secure session management
- **Modern Glassmorphic UI**: 
  - Multi-row, responsive card layout
  - Real-time client-side search and filtering
  - Smooth animations and hover effects
- **Import & Export**: 
  - CSV import from Bitwarden, LastPass, and other managers
  - Bulk import with duplicate detection
  - Secure password generation
- **Smart Features**:
  - One-click copy to clipboard
  - Show/hide password functionality
  - Entry count and search result tracking
  - Only shows entries decryptable with correct master password

### 📊 **Real-Time System Monitoring**
- **Cross-Platform Monitoring**: 
  - **Windows & Linux Support**: Native system monitoring for both platforms
  - **Real-Time Metrics**: CPU, Memory, Disk, and Network usage
  - **Live Updates**: Auto-refresh every 30 seconds with manual refresh option
- **Comprehensive Statistics**:
  - **CPU**: Usage percentage, core count, frequency, load average (Linux)
  - **Memory**: Total/used/available RAM, swap usage, percentage utilization
  - **Storage**: Multi-disk support, usage percentages, free space tracking
  - **Network**: Bandwidth monitoring, interface details, data transfer statistics
- **Visual Dashboard**:
  - Animated progress bars with status color coding
  - System status badges (Good/Warning/Critical)
  - Detailed system information panel
  - Last updated timestamps

### 👤 **User Management & Security**
- **Secure Authentication System**: 
  - User registration and login with Django's built-in security
  - Session management with automatic logout
  - Password validation and security best practices
- **Individual User Spaces**: 
  - Personal password vaults
  - User-specific media libraries
  - Individual system preferences

### 🎨 **Premium User Experience**
- **Modern Design Language**: 
  - Glassmorphism effects with subtle transparency
  - Smooth animations and micro-interactions
  - Dark theme with beautiful gradient backgrounds
- **Responsive Interface**: 
  - Mobile-first design that works on all devices
  - Touch-friendly controls and optimized layouts
  - Consistent visual hierarchy across all modules
- **Performance Optimized**: 
  - Lazy loading and efficient data fetching
  - Debounced search inputs
  - Background task processing with Celery

## 🛠️ Technical Architecture

### **Core Technologies**
- **Backend Framework**: Django 5.2+ (Python web framework)
- **Frontend Stack**: Bootstrap 5, Vanilla JavaScript, Font Awesome icons
- **Database**: SQLite (default) with PostgreSQL/MySQL support
- **Task Queue**: Celery with Redis for background processing
- **System Monitoring**: psutil for cross-platform system metrics
- **Security**: AES-256 encryption, CSRF protection, secure sessions

### **External Integrations**
- **Torrent Engine**: qBittorrent Web API integration
- **Media Processing**: FFmpeg for video transcoding and HLS streaming
- **Caching**: Redis for session storage and task queue
- **Web Scraping**: Custom scrapers for multiple torrent sites

### **Project Structure**
```
DineriServer/
├── apps/
│   ├── dashboard/          # Main dashboard with system monitoring
│   │   ├── services/       # System monitoring service
│   │   └── views.py        # Real-time stats API
│   ├── search/             # Multi-source torrent search
│   │   ├── services/       # Search scrapers and aggregation
│   │   └── forms.py        # Search forms and filters
│   ├── torrents/           # Torrent management and monitoring
│   │   ├── services/       # qBittorrent API integration
│   │   └── models.py       # Torrent data models
│   ├── mediahub/           # Media organization and streaming
│   │   ├── models.py       # Media file models
│   │   └── tasks.py        # Background media processing
│   ├── passwordmanager/    # Secure password vault
│   │   ├── services/       # Encryption and CSV import services
│   │   ├── models.py       # Encrypted password storage
│   │   └── forms.py        # Password management forms
│   └── accounts/           # User authentication and management
├── homeserver/             # Django project configuration
│   ├── settings.py         # Application settings
│   ├── celery.py          # Celery configuration
│   └── urls.py            # URL routing
├── static/                 # Static assets (CSS, JS, images)
│   ├── css/               # Modern styling with glassmorphism
│   └── js/                # Interactive frontend functionality
└── templates/             # HTML templates with modern UI
    ├── base.html          # Base template with responsive layout
    └── [app_templates]/   # App-specific templates
```

### **Key Features by Module**

#### **Dashboard (`apps/dashboard/`)**
- Real-time system monitoring with `psutil`
- Cross-platform support (Windows/Linux)
- RESTful API for live statistics
- Modern glassmorphic dashboard interface

#### **Password Manager (`apps/passwordmanager/`)**
- AES-256 encryption with Argon2 key derivation
- CSV import/export with duplicate detection
- Modern multi-row card interface
- Client-side search and filtering

#### **Search Engine (`apps/search/`)**
- Multi-threaded web scraping
- Result aggregation and deduplication
- Advanced filtering and sorting
- Source-specific customization

#### **Media Hub (`apps/mediahub/`)**
- Automatic HLS transcoding
- Responsive video streaming
- Media metadata extraction
- Grid-based media browser

#### **Torrent Management (`apps/torrents/`)**
- qBittorrent Web API integration
- Real-time status monitoring
- Background task processing
- Download queue management

## 🚀 Installation & Setup

### **Prerequisites**
- **Python 3.8+** with pip
- **qBittorrent** with Web UI enabled (default port 8090)
- **FFmpeg** for media transcoding
- **Redis** for task queue and caching
- **Internet connection** for torrent site scraping

### **Quick Installation**

1. **Clone and Setup**
   ```bash
   git clone [repository-url]
   cd DineriServer
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure External Services**
   ```bash
   # Install qBittorrent and enable Web UI on port 8090
   # Install FFmpeg and ensure it's in your PATH
   # Start Redis server
   docker run -p 6379:6379 -d redis:alpine
   # Or install Redis natively on your system
   ```

3. **Initialize Database**
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   python manage.py createsuperuser  # Optional: create admin user
   ```

4. **Start Background Services**
   ```bash
   # Terminal 1: Celery Worker
   celery -A homeserver worker --loglevel=info
   
   # Terminal 2: Celery Beat Scheduler  
   celery -A homeserver beat --loglevel=info
   ```

5. **Launch the Server**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

6. **Access Your Server**
   - Open browser to `http://localhost:8000`
   - Create user account
   - Start using all features!

### **Configuration Options**

#### **Environment Variables** (`.env` file)
```env
# Database
DATABASE_URL=sqlite:///db.sqlite3

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# qBittorrent Settings
QBITTORRENT_HOST=localhost
QBITTORRENT_PORT=8090
QBITTORRENT_USERNAME=admin
QBITTORRENT_PASSWORD=adminpass

# Security Settings
SECRET_KEY=your-secret-key-here
DEBUG=False

# Media Processing
FFMPEG_PATH=/usr/bin/ffmpeg
```

#### **System Requirements**
- **Memory**: 2GB+ RAM recommended
- **Storage**: 10GB+ free space for media
- **CPU**: Multi-core recommended for transcoding
- **Network**: Stable internet for torrent searching

## 🔧 Advanced Configuration

### **Production Deployment**
- Use PostgreSQL/MySQL for production database
- Configure nginx/Apache as reverse proxy
- Set up SSL certificates for HTTPS
- Use systemd/supervisor for service management
- Configure firewall rules appropriately

### **Security Considerations**
- Change default secret keys and passwords
- Enable HTTPS in production
- Regularly update dependencies
- Monitor system logs for suspicious activity
- Use strong master passwords for vault

### **Performance Tuning**
- Adjust Celery worker count based on CPU cores
- Configure Redis memory limits
- Set up media caching strategies
- Optimize database queries and indexing

## 📱 Usage Examples

### **System Monitoring**
- View real-time CPU, memory, disk, and network statistics
- Monitor system health with color-coded status indicators
- Track system uptime and performance trends
- Get detailed information about storage devices and network interfaces

### **Password Management**
- Store all your passwords in one secure location
- Import existing passwords from other managers via CSV
- Search and filter passwords by site name, username, or URL
- Copy credentials to clipboard with one click

### **Media Streaming**
- Search for content across multiple torrent sites
- Download directly through the web interface
- Automatically organize and transcode media files
- Stream content to any device with HLS support

## 🤝 Contributing

This is a personal project, but suggestions and feedback are welcome! Please ensure any contributions align with the project's focus on personal, non-commercial use.

## 📝 License

**Personal Use Only** - This project is intended for personal, educational, and non-commercial use only. 

## ⚠️ Legal Disclaimer

This software is designed for downloading freely available content or content you have the legal right to download. Users are solely responsible for ensuring their use complies with local laws and regulations regarding content downloading and sharing.

## 🔗 Contact

**Created by Rayen Guermazi**

Feel free to reach out with questions, suggestions, or feedback!

---

*Dineri Server - Your complete home server solution* 🏠✨
