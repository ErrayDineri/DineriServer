# 🚀 Quick Setup Guide

This is a simplified setup guide for new users.

## Step 1: Prerequisites

Make sure you have:
- **Docker Desktop** installed and running
- **Git** for cloning the repository
- A text editor to modify configuration files

## Step 2: Download and Configure

1. **Download the project**:
   ```bash
   git clone [your-repository-url]
   cd DineriServer
   ```

2. **Set up your passwords**:
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file and change these important passwords:
   - `DB_PASSWORD` - Database password
   - `QB_PASSWORD` - qBittorrent password  
   - `SECRET_KEY` - Django security key (make it long and random)
   - `DJANGO_SUPERUSER_PASSWORD` - Admin account password

## Step 3: Start Everything

```bash
docker-compose up -d
```

Wait a minute for everything to start, then check status:
```bash
docker-compose ps
```

## Step 4: Access Your Server

- **Main App**: http://localhost
- **qBittorrent**: http://localhost:8080

## Step 5: First Login

1. Go to http://localhost
2. Create a new user account or use the admin account if configured
3. Start using all the features!

## What's Running?

- **Web Server** (Port 80): Main application with nice interface
- **Django** (Port 8000): Backend API and admin
- **qBittorrent** (Port 8080): Torrent client web interface
- **Database**: PostgreSQL (internal)
- **Cache**: Redis (internal)
- **Background Tasks**: Celery workers (internal)

## Need Help?

- Check logs: `docker-compose logs web`
- Stop everything: `docker-compose down`
- Update: `git pull && docker-compose up -d --build`

## Security Notes

- Change default passwords in `.env` file
- Don't expose to internet without proper security
- Keep the system updated
- Use strong passwords for your user accounts
