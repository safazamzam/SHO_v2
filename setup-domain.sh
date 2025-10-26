#!/bin/bash

# Domain Setup Script for Shift Handover App
# This script helps you set up domain name access with SSL certificates

set -e

echo "🌐 Shift Handover App - Domain Setup Script"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running on the server
if [[ ! -f "docker-compose.yml" ]]; then
    print_error "This script must be run from the project directory containing docker-compose.yml"
    exit 1
fi

echo
print_info "This script will help you set up domain access for your Shift Handover application."
print_info "Make sure you have:"
print_info "1. A domain name pointing to this server's IP (35.200.202.18)"
print_info "2. DNS A record configured"
print_info "3. Ports 80 and 443 open in your firewall"
echo

# Get domain name from user
read -p "Enter your domain name (e.g., handover.yourdomain.com): " DOMAIN_NAME
if [[ -z "$DOMAIN_NAME" ]]; then
    print_error "Domain name is required!"
    exit 1
fi

# Get email for Let's Encrypt
read -p "Enter your email for SSL certificate notifications: " EMAIL
if [[ -z "$EMAIL" ]]; then
    print_error "Email is required for SSL certificates!"
    exit 1
fi

print_info "Setting up domain: $DOMAIN_NAME"
print_info "Email: $EMAIL"

# Create environment file
cat > .env.domain << EOF
DOMAIN_NAME=$DOMAIN_NAME
EMAIL=$EMAIL
FLASK_ENV=production
FLASK_DEBUG=0
NGINX_WORKER_PROCESSES=auto
NGINX_WORKER_CONNECTIONS=1024
EOF

print_status "Created .env.domain file"

# Update nginx configuration with actual domain
sed -i "s/your-domain.com/$DOMAIN_NAME/g" nginx/conf.d/app.conf

print_status "Updated nginx configuration with your domain"

# Check if SSL certificates exist
if [[ ! -d "/etc/letsencrypt/live/$DOMAIN_NAME" ]]; then
    print_warning "SSL certificates not found. You'll need to obtain them first."
    
    echo
    print_info "To get SSL certificates, run these commands:"
    echo
    echo "1. First, start nginx without SSL:"
    echo "   docker-compose -f docker-compose.prod.yml up -d nginx"
    echo
    echo "2. Get SSL certificate:"
    echo "   docker run --rm -v \$(pwd)/certbot_conf:/etc/letsencrypt -v \$(pwd)/certbot_www:/var/www/certbot certbot/certbot certonly --webroot --webroot-path=/var/www/certbot --email $EMAIL --agree-tos --no-eff-email -d $DOMAIN_NAME"
    echo
    echo "3. Restart with SSL:"
    echo "   docker-compose -f docker-compose.prod.yml down"
    echo "   docker-compose -f docker-compose.prod.yml up -d"
    echo
fi

# Create SSL setup script
cat > setup-ssl.sh << 'EOF'
#!/bin/bash

# SSL Certificate Setup Script
# Run this after the nginx service is running

set -e

source .env.domain

echo "🔒 Setting up SSL certificate for $DOMAIN_NAME"

# Create directories
mkdir -p certbot_conf certbot_www

# Stop any existing services
docker-compose -f docker-compose.prod.yml down || true

# Start nginx in HTTP-only mode first
echo "Starting nginx in HTTP mode..."
docker-compose -f docker-compose.prod.yml up -d db web

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Start nginx without SSL first
docker run --rm -d --name nginx-temp \
  -p 80:80 \
  -v $(pwd)/nginx/nginx.conf:/etc/nginx/nginx.conf:ro \
  -v $(pwd)/certbot_www:/var/www/certbot \
  --network $(basename $(pwd))_app_network \
  nginx:alpine

# Obtain SSL certificate
echo "Obtaining SSL certificate from Let's Encrypt..."
docker run --rm \
  -v $(pwd)/certbot_conf:/etc/letsencrypt \
  -v $(pwd)/certbot_www:/var/www/certbot \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email $EMAIL \
  --agree-tos \
  --no-eff-email \
  -d $DOMAIN_NAME

# Stop temporary nginx
docker stop nginx-temp || true

# Start full stack with SSL
echo "Starting full stack with SSL..."
docker-compose -f docker-compose.prod.yml up -d

echo "✅ SSL setup complete!"
echo "🌐 Your application should now be available at: https://$DOMAIN_NAME"
EOF

chmod +x setup-ssl.sh

print_status "Created SSL setup script: setup-ssl.sh"

# Create simple deployment script
cat > deploy-with-domain.sh << 'EOF'
#!/bin/bash

# Deploy Shift Handover App with Domain Support

set -e

echo "🚀 Deploying Shift Handover App with Domain Support"

# Load environment
if [[ -f ".env.domain" ]]; then
    source .env.domain
    echo "✅ Loaded domain configuration"
else
    echo "❌ .env.domain file not found. Run setup-domain.sh first."
    exit 1
fi

# Pull latest images
echo "📦 Pulling latest Docker images..."
docker-compose -f docker-compose.prod.yml pull

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose -f docker-compose.prod.yml down

# Start services
echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check health
echo "🏥 Checking service health..."
docker-compose -f docker-compose.prod.yml ps

echo
echo "✅ Deployment complete!"
echo "🌐 Application available at:"
echo "   HTTP:  http://$DOMAIN_NAME (redirects to HTTPS)"
echo "   HTTPS: https://$DOMAIN_NAME"
echo
echo "📊 To check logs:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"
EOF

chmod +x deploy-with-domain.sh

print_status "Created deployment script: deploy-with-domain.sh"

echo
echo "🎉 Domain setup preparation complete!"
echo
print_info "Next steps:"
echo "1. Make sure your domain $DOMAIN_NAME points to this server (35.200.202.18)"
echo "2. Run: ./setup-ssl.sh (to get SSL certificates)"
echo "3. Run: ./deploy-with-domain.sh (to deploy with domain support)"
echo
print_warning "Important: Make sure DNS is configured before running SSL setup!"
echo
echo "To check DNS configuration:"
echo "  nslookup $DOMAIN_NAME"
echo "  dig $DOMAIN_NAME"
echo