#!/bin/bash
# Helper script to set up the Docker environment for Dineri Server

set -e

# Create necessary directories
echo "Creating directory structure..."
mkdir -p config/nginx
mkdir -p config/qbittorrent
mkdir -p data
mkdir -p media/downloads

# Copy configuration files if they don't exist
if [ ! -f "config/nginx/dineri.conf" ]; then
    echo "Creating Nginx configuration..."
    cp docker-resources/dineri.conf config/nginx/
fi

# Copy Docker settings file if it doesn't exist
if [ -f "docker-resources/settings_docker.py" ] && [ ! -f "homeserver/settings_docker.py" ]; then
    echo "Copying Docker settings file..."
    cp docker-resources/settings_docker.py homeserver/
fi

# Check if .env file exists, create if it doesn't
if [ ! -f ".env" ]; then
    echo "Creating .env file with random secret key..."
    # Generate a random secret key
    SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')
    cat > .env << EOF
# Database
DB_PASSWORD=secure_database_password

# qBittorrent
QB_USERNAME=admin
QB_PASSWORD=adminpassword

# Django
SECRET_KEY=${SECRET_KEY}
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=admin_password
DJANGO_SUPERUSER_EMAIL=admin@example.com
EOF
    echo ".env file created with random secret key. Please update passwords before deployment!"
else
    echo ".env file already exists."
fi

echo "Setting correct permissions..."
chmod +x docker-entrypoint.sh

echo "Setup complete! You can now run 'docker-compose up -d' to start Dineri Server."
echo "For development, use 'docker-compose -f docker-compose.yml -f docker-compose.override.yml up'"