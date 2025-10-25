#!/bin/bash

# Quick HTTPS setup for testing with self-signed certificates
echo "🚀 Quick HTTPS Setup with Self-Signed Certificates"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Get domain or use localhost
read -p "🌐 Enter your domain name (or press Enter for localhost): " DOMAIN_NAME
DOMAIN_NAME=${DOMAIN_NAME:-localhost}

echo "🔧 Setting up HTTPS for: $DOMAIN_NAME"

# Create certificates directory
mkdir -p certs

# Generate self-signed certificate
echo "🔐 Generating self-signed SSL certificate..."
openssl req -x509 -newkey rsa:4096 -nodes \
    -out certs/cert.pem \
    -keyout certs/key.pem \
    -days 365 \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN_NAME"

# Create simple environment file
cat > .env.https << EOF
FLASK_ENV=production
SECRET_KEY=$(openssl rand -base64 32)
DOMAIN_NAME=$DOMAIN_NAME
USE_LETSENCRYPT=false
USE_GUNICORN=true
SSL_CERT_PATH=/app/certs/cert.pem
SSL_KEY_PATH=/app/certs/key.pem
DATABASE_URI=sqlite:///instance/shift_handover.db
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SERVICENOW_ENABLED=false
SSO_ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null || echo "change-this-key")
SECRETS_MASTER_KEY=$(openssl rand -base64 32)
PORT=5000
WORKERS=2
LOG_LEVEL=INFO
EOF

# Create simple docker-compose for self-signed HTTPS
cat > docker-compose.quick-https.yml << 'EOF'
version: '3.8'

services:
  web:
    build: .
    command: flask run --host=0.0.0.0 --port=5000 --cert=/app/certs/cert.pem --key=/app/certs/key.pem
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./certs:/app/certs:ro
      - app_data:/app/instance
    env_file:
      - .env.https
    restart: unless-stopped

volumes:
  app_data:
EOF

# Build and start the service
echo "🏗️ Building and starting HTTPS service..."
docker-compose -f docker-compose.quick-https.yml up --build -d

# Wait for service to start
sleep 5

# Check if service is running
if docker-compose -f docker-compose.quick-https.yml ps | grep -q "Up"; then
    echo ""
    echo "✅ HTTPS Setup Complete!"
    echo "========================"
    echo "🌐 Your application is now available at: https://$DOMAIN_NAME:5000"
    echo "⚠️  Browser will show security warning (self-signed certificate)"
    echo "📊 Check logs with: docker-compose -f docker-compose.quick-https.yml logs -f"
    echo ""
    echo "🔧 Useful Commands:"
    echo "- Stop: docker-compose -f docker-compose.quick-https.yml down"
    echo "- Restart: docker-compose -f docker-compose.quick-https.yml restart"
    echo "- Logs: docker-compose -f docker-compose.quick-https.yml logs -f web"
    echo ""
    echo "📝 Next Steps:"
    echo "1. For production, use the full HTTPS setup with Let's Encrypt"
    echo "2. Update .env.https with your SMTP and database credentials"
    echo "3. Configure your domain to point to this server"
else
    echo "❌ Failed to start HTTPS service. Check logs:"
    docker-compose -f docker-compose.quick-https.yml logs
fi