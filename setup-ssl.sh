#!/bin/bash

# SSL Certificate Setup Script for Let's Encrypt
# This script helps set up SSL certificates for your domain

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔒 Shift Handover App - HTTPS Setup Script${NC}"
echo "=============================================="

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo -e "${RED}❌ Error: .env.production file not found${NC}"
    echo -e "${YELLOW}Please copy .env.production.template to .env.production and configure your settings${NC}"
    exit 1
fi

# Source environment variables
source .env.production

# Validate required variables
if [ -z "$DOMAIN_NAME" ] || [ -z "$CERTBOT_EMAIL" ]; then
    echo -e "${RED}❌ Error: DOMAIN_NAME and CERTBOT_EMAIL must be set in .env.production${NC}"
    exit 1
fi

echo -e "${GREEN}📋 Configuration:${NC}"
echo "   Domain: $DOMAIN_NAME"
echo "   Email: $CERTBOT_EMAIL"
echo ""

# Create necessary directories
echo -e "${GREEN}📁 Creating SSL directories...${NC}"
mkdir -p ./certbot/conf
mkdir -p ./certbot/www
mkdir -p ./nginx/ssl

# Generate DH parameters for better security (this may take a while)
if [ ! -f "./nginx/ssl/dhparam.pem" ]; then
    echo -e "${GREEN}🔐 Generating DH parameters (this may take a few minutes)...${NC}"
    openssl dhparam -out ./nginx/ssl/dhparam.pem 2048
    echo -e "${GREEN}✅ DH parameters generated${NC}"
fi

# Create temporary nginx config for initial certificate request
echo -e "${GREEN}📝 Creating temporary nginx configuration...${NC}"
cat > ./nginx/conf.d/temp.conf << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 200 'Temporary server for SSL setup';
        add_header Content-Type text/plain;
    }
}
EOF

# Start temporary containers for certificate generation
echo -e "${GREEN}🐳 Starting temporary containers...${NC}"
docker-compose -f docker-compose.https.yml up -d nginx

# Wait for nginx to be ready
echo -e "${GREEN}⏳ Waiting for nginx to be ready...${NC}"
sleep 10

# Request SSL certificate
echo -e "${GREEN}🔒 Requesting SSL certificate from Let's Encrypt...${NC}"
docker-compose -f docker-compose.https.yml run --rm certbot \
    certonly --webroot \
    --webroot-path=/var/www/certbot \
    --email $CERTBOT_EMAIL \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d $DOMAIN_NAME \
    -d www.$DOMAIN_NAME

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ SSL certificate successfully obtained!${NC}"
    
    # Remove temporary config
    rm -f ./nginx/conf.d/temp.conf
    
    # Replace domain placeholder in nginx config
    sed -i "s/\${DOMAIN_NAME}/$DOMAIN_NAME/g" ./nginx/conf.d/https.conf
    
    echo -e "${GREEN}🔄 Restarting containers with SSL configuration...${NC}"
    docker-compose -f docker-compose.https.yml down
    docker-compose -f docker-compose.https.yml up -d
    
    echo ""
    echo -e "${GREEN}🎉 SSL setup completed successfully!${NC}"
    echo -e "${GREEN}Your application is now available at: https://$DOMAIN_NAME${NC}"
    echo ""
    echo -e "${YELLOW}📝 Next steps:${NC}"
    echo "   1. Test your application: https://$DOMAIN_NAME"
    echo "   2. Check SSL rating: https://www.ssllabs.com/ssltest/"
    echo "   3. Set up automatic certificate renewal (already configured)"
    echo ""
    
else
    echo -e "${RED}❌ Failed to obtain SSL certificate${NC}"
    echo -e "${YELLOW}Please check:${NC}"
    echo "   1. Domain DNS is pointing to your server"
    echo "   2. Port 80 is accessible from the internet"
    echo "   3. No firewall blocking the connection"
    exit 1
fi

# Setup auto-renewal check
echo -e "${GREEN}📅 Setting up certificate auto-renewal...${NC}"
(crontab -l 2>/dev/null; echo "0 12 * * * cd $(pwd) && docker-compose -f docker-compose.https.yml exec certbot certbot renew --quiet && docker-compose -f docker-compose.https.yml exec nginx nginx -s reload") | crontab -

echo -e "${GREEN}✅ Auto-renewal configured${NC}"
echo -e "${GREEN}🔒 HTTPS setup complete!${NC}"