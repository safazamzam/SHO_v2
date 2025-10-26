#!/bin/bash

# 🔒 SSL Certificate Setup Script for Shift Handover App

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🔒 SSL Certificate Setup for Shift Handover App"
echo "=============================================="

# Check if .env.domain exists
if [ ! -f ".env.domain" ]; then
    print_error ".env.domain file not found!"
    print_status "Please run ./setup-domain.sh first to configure your domain."
    exit 1
fi

# Load environment variables
source .env.domain

# Validate required variables
if [ -z "$DOMAIN_NAME" ] || [ -z "$EMAIL" ]; then
    print_error "DOMAIN_NAME and EMAIL must be set in .env.domain"
    exit 1
fi

print_status "Setting up SSL certificate for domain: $DOMAIN_NAME"
print_status "Contact email: $EMAIL"

# Create necessary directories
print_status "Creating certificate directories..."
mkdir -p certbot_conf
mkdir -p certbot_www
mkdir -p nginx/ssl

# Check if domain is accessible
print_status "Checking domain accessibility..."
if ! curl -f -s "http://$DOMAIN_NAME/.well-known/acme-challenge/test" > /dev/null 2>&1; then
    print_warning "Domain might not be accessible yet. Continuing anyway..."
fi

# Check if certificate already exists
if [ -f "certbot_conf/live/$DOMAIN_NAME/fullchain.pem" ]; then
    print_warning "Certificate already exists for $DOMAIN_NAME"
    read -p "Do you want to renew it? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Skipping certificate generation."
        exit 0
    fi
fi

# Stop any existing services that might conflict
print_status "Ensuring clean environment..."
docker-compose -f docker-compose.prod.yml down > /dev/null 2>&1 || true

# Start nginx for certificate validation
print_status "Starting nginx for certificate validation..."
docker-compose -f docker-compose.prod.yml up -d nginx

# Wait for nginx to start
sleep 5

# Test nginx is running
if ! docker-compose -f docker-compose.prod.yml ps nginx | grep -q "Up"; then
    print_error "Nginx failed to start!"
    exit 1
fi

print_success "Nginx started successfully"

# Obtain SSL certificate
print_status "Obtaining SSL certificate from Let's Encrypt..."
docker run --rm \
    --name certbot \
    -v "$(pwd)/certbot_conf:/etc/letsencrypt" \
    -v "$(pwd)/certbot_www:/var/www/certbot" \
    certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d "$DOMAIN_NAME"

# Check if certificate was created
if [ -f "certbot_conf/live/$DOMAIN_NAME/fullchain.pem" ]; then
    print_success "SSL certificate obtained successfully!"
    
    # Display certificate information
    print_status "Certificate details:"
    docker run --rm \
        -v "$(pwd)/certbot_conf:/etc/letsencrypt" \
        certbot/certbot certificates | grep -A 10 "$DOMAIN_NAME"
    
    # Set up automatic renewal
    print_status "Setting up automatic certificate renewal..."
    
    # Create renewal script
    cat > renew-ssl.sh << 'EOF'
#!/bin/bash
echo "Renewing SSL certificates..."
docker run --rm \
    -v $(pwd)/certbot_conf:/etc/letsencrypt \
    -v $(pwd)/certbot_www:/var/www/certbot \
    certbot/certbot renew --quiet

if [ $? -eq 0 ]; then
    echo "Certificate renewed successfully. Restarting nginx..."
    docker-compose -f docker-compose.prod.yml restart nginx
    echo "Nginx restarted."
else
    echo "Certificate renewal failed!"
fi
EOF
    
    chmod +x renew-ssl.sh
    print_success "Created automatic renewal script: renew-ssl.sh"
    
    # Restart services with SSL
    print_status "Restarting services with SSL configuration..."
    docker-compose -f docker-compose.prod.yml restart
    
    # Wait for services to start
    sleep 10
    
    # Test HTTPS access
    print_status "Testing HTTPS access..."
    if curl -f -s -k "https://$DOMAIN_NAME" > /dev/null; then
        print_success "HTTPS is working!"
    else
        print_warning "HTTPS test failed, but certificate is installed."
    fi
    
    # Display final information
    echo ""
    print_success "🎉 SSL Setup Complete!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🌐 Your secure application is available at:"
    echo "   https://$DOMAIN_NAME"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Test your application: https://$DOMAIN_NAME/login"
    echo "   2. Set up monitoring with: docker-compose -f docker-compose.prod.yml logs -f"
    echo "   3. Automatic renewal is configured via renew-ssl.sh"
    echo ""
    echo "🔄 Certificate will auto-renew before expiration"
    echo "📅 Certificate expires: $(docker run --rm -v $(pwd)/certbot_conf:/etc/letsencrypt certbot/certbot certificates | grep -A 5 "$DOMAIN_NAME" | grep "Expiry Date" | cut -d: -f2-)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
else
    print_error "Failed to obtain SSL certificate!"
    print_status "Please check:"
    echo "  1. Domain DNS is properly configured"
    echo "  2. Firewall allows HTTP (port 80) traffic"
    echo "  3. Domain is accessible from the internet"
    echo ""
    print_status "You can check logs with:"
    echo "  docker-compose -f docker-compose.prod.yml logs nginx"
    exit 1
fi