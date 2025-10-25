#!/bin/bash

# HTTPS Deployment Script for Cloud VM
# This script sets up your Flask application with HTTPS support

set -e  # Exit on any error

echo "🚀 HTTPS Deployment Setup for Shift Handover Application"
echo "========================================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run this script as root (sudo)"
    exit 1
fi

# Get domain name from user
read -p "🌐 Enter your domain name (e.g., myapp.example.com): " DOMAIN_NAME
read -p "📧 Enter your email for Let's Encrypt: " EMAIL

if [ -z "$DOMAIN_NAME" ] || [ -z "$EMAIL" ]; then
    echo "❌ Domain name and email are required!"
    exit 1
fi

echo "🔧 Setting up for domain: $DOMAIN_NAME"

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install Docker and Docker Compose if not installed
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    usermod -aG docker $USER
fi

if ! command -v docker-compose &> /dev/null; then
    echo "🔗 Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Create application directory
APP_DIR="/opt/shift-handover"
echo "📁 Creating application directory: $APP_DIR"
mkdir -p $APP_DIR
cd $APP_DIR

# Clone or copy your application
if [ ! -f "app.py" ]; then
    echo "📥 Please copy your application files to $APP_DIR"
    echo "Or clone from GitLab:"
    echo "git clone https://git.garage.epam.com/shift-handover-automation/shifthandover.git ."
    exit 1
fi

# Create environment file
echo "⚙️ Creating environment configuration..."
cat > .env.https << EOF
FLASK_ENV=production
SECRET_KEY=$(openssl rand -base64 32)
DOMAIN_NAME=$DOMAIN_NAME
CERTBOT_EMAIL=$EMAIL
USE_LETSENCRYPT=true
USE_GUNICORN=true
DATABASE_URI=sqlite:///instance/shift_handover.db
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SERVICENOW_ENABLED=false
SSO_ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
SECRETS_MASTER_KEY=$(openssl rand -base64 32)
PORT=5000
WORKERS=4
LOG_LEVEL=INFO
EOF

# Create nginx configuration with domain
echo "🌐 Creating Nginx configuration..."
mkdir -p nginx/conf.d
sed "s/\${DOMAIN_NAME}/$DOMAIN_NAME/g" nginx/conf.d/app.conf > nginx/conf.d/app.conf.tmp
mv nginx/conf.d/app.conf.tmp nginx/conf.d/app.conf

# Create directories for Let's Encrypt
mkdir -p certbot/conf certbot/www

# Initial certificate request (HTTP challenge)
echo "🔐 Requesting SSL certificate from Let's Encrypt..."
docker-compose -f docker-compose.https.yml up -d nginx

# Wait for nginx to start
sleep 10

# Get initial certificate
docker-compose -f docker-compose.https.yml run --rm certbot \
    certonly --webroot --webroot-path=/var/www/certbot \
    --email $EMAIL --agree-tos --no-eff-email \
    -d $DOMAIN_NAME

# Restart nginx with SSL
echo "🔄 Restarting services with SSL..."
docker-compose -f docker-compose.https.yml down
docker-compose -f docker-compose.https.yml up -d

# Setup certificate renewal
echo "⚡ Setting up automatic certificate renewal..."
cat > /etc/cron.d/certbot-renewal << EOF
0 12 * * * root docker-compose -f $APP_DIR/docker-compose.https.yml run --rm certbot renew --quiet && docker-compose -f $APP_DIR/docker-compose.https.yml exec nginx nginx -s reload
EOF

# Configure firewall (if ufw is installed)
if command -v ufw &> /dev/null; then
    echo "🔥 Configuring firewall..."
    ufw allow 22/tcp   # SSH
    ufw allow 80/tcp   # HTTP
    ufw allow 443/tcp  # HTTPS
    ufw --force enable
fi

echo ""
echo "✅ HTTPS Deployment Complete!"
echo "==============================="
echo "🌐 Your application is now available at: https://$DOMAIN_NAME"
echo "🔒 SSL certificate auto-renewal is configured"
echo "📊 Check logs with: docker-compose -f $APP_DIR/docker-compose.https.yml logs"
echo ""
echo "⚠️  Important Notes:"
echo "1. Make sure your domain DNS points to this server's IP"
echo "2. Update your .env.https file with proper SMTP/database credentials"
echo "3. Restart services after config changes: docker-compose -f $APP_DIR/docker-compose.https.yml restart"
echo ""
echo "🔧 Useful Commands:"
echo "- View logs: docker-compose logs -f"
echo "- Restart: docker-compose restart"
echo "- Update app: git pull && docker-compose up --build -d"