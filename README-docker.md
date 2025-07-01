# 🐳 Dineri Server Docker Deployment

This guide explains how to deploy Dineri Server using Docker.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose v2.x installed
- Git
- Basic understanding of Docker containers

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/dineri-server.git
cd dineri-server
```

2. **Run the setup script**
```bash
chmod +x docker-setup.sh
./docker-setup.sh
```

3. **Edit the .env file** with your secure passwords

4. **Start the containers**
```bash
docker-compose up -d
```

5. **Access Dineri Server**
- Main application: http://localhost:80
- qBittorrent: http://localhost:8080

## 🔧 Configuration

### Environment Variables

Edit the `.env` file to configure:

- Database passwords
- qBittorrent credentials
- Django secret key and admin account

### Data Persistence

Your data is stored in:

- `./data`: Database files
- `./media`: Media files, downloads
- `./config`: Configuration files

## 🛠️ Maintenance

### Updating

```bash
git pull
docker-compose build
docker-compose down
docker-compose up -d
```

### Backups

```bash
# Database backup
docker-compose exec db pg_dump -U dineri dineri > backup_$(date +%Y%m%d).sql

# Configuration and media backup
tar -czf dineri_backup_$(date +%Y%m%d).tar.gz ./config ./media ./data
```

### Logs

```bash
docker-compose logs -f web
```

## 🔍 Troubleshooting

### Common Issues

1. **Can't connect to the application**
   - Check if all containers are running: `docker-compose ps`
   - Check logs for errors: `docker-compose logs web`

2. **Database connection issues**
   - Ensure PostgreSQL is running: `docker-compose logs db`
   - Verify database credentials in `.env`

3. **Media file permissions**
   - Fix permissions: `sudo chown -R 1000:1000 ./media`

## 🔒 Security

### Production Configuration

1. **Environment Security**:
   - Set strong passwords in `.env`
   - Update `ALLOWED_HOSTS` in environment variables
   - Set `DEBUG=False` for production

2. **SSL Configuration**:
   - Create a directory for SSL certificates:
     ```bash
     mkdir -p config/nginx/ssl
     ```
   
   - Generate self-signed certificates (for testing):
     ```bash
     openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
       -keyout config/nginx/ssl/dineri.key \
       -out config/nginx/ssl/dineri.crt
     ```
   
   - For production, use Let's Encrypt:
     ```bash
     # Install certbot on your host
     certbot certonly --standalone -d yourdomain.com
     
     # Copy certificates to Nginx config directory
     cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem config/nginx/ssl/dineri.crt
     cp /etc/letsencrypt/live/yourdomain.com/privkey.pem config/nginx/ssl/dineri.key
     ```
   
   - Update Nginx configuration:
     ```bash
     # Create SSL config file
     cp docker-resources/nginx-ssl.conf config/nginx/dineri.conf
     ```

3. **Network Security**:
   - Consider running behind a reverse proxy
   - Set up proper firewall rules
   - Limit exposed ports:
     ```bash
     # Only expose necessary ports
     ufw allow 80,443/tcp
     ufw deny 8000,8080,5432/tcp
     ```

## 📚 Advanced Usage

### Development Mode

```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up
```

### Scaling Workers

```bash
docker-compose up -d --scale worker=3
```

### Container Monitoring

```bash
# Monitor container resource usage
docker stats

# View container logs in real-time
docker-compose logs -f

# Check container health
docker inspect --format='{{json .State.Health}}' dineri-server_web_1
```

### Database Management

```bash
# Access PostgreSQL
docker-compose exec db psql -U dineri -d dineri

# Run Django management commands
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py createsuperuser
```