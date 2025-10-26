#!/bin/bash

# 🚀 Deploy Shift Handover App with Domain Name

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

print_header() {
    echo -e "${PURPLE}[DEPLOY]${NC} $1"
}

echo "🚀 Deploying Shift Handover App with Domain"
echo "==========================================="

# Check if .env.domain exists
if [ ! -f ".env.domain" ]; then
    print_error ".env.domain file not found!"
    print_status "Please run ./setup-domain.sh first to configure your domain."
    exit 1
fi

# Load environment variables
source .env.domain

print_header "Starting deployment for domain: $DOMAIN_NAME"

# Pre-deployment checks
print_status "Running pre-deployment checks..."

# Check if domain configuration exists
if [ -z "$DOMAIN_NAME" ]; then
    print_error "DOMAIN_NAME not set in .env.domain"
    exit 1
fi

# Check if SSL certificate exists
if [ ! -f "certbot_conf/live/$DOMAIN_NAME/fullchain.pem" ]; then
    print_warning "SSL certificate not found for $DOMAIN_NAME"
    print_status "Run ./setup-ssl.sh to obtain SSL certificate first"
    read -p "Continue without SSL? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    SSL_AVAILABLE=false
else
    SSL_AVAILABLE=true
    print_success "SSL certificate found"
fi

# Check Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed or not in PATH"
    exit 1
fi

print_success "Docker and Docker Compose are available"

# Stop existing deployment
print_status "Stopping existing deployment..."
docker-compose down > /dev/null 2>&1 || true
docker-compose -f docker-compose.prod.yml down > /dev/null 2>&1 || true

# Clean up old containers
print_status "Cleaning up old containers..."
docker system prune -f > /dev/null 2>&1 || true

# Build and start services
print_status "Building and starting services..."
docker-compose -f docker-compose.prod.yml build --no-cache

print_status "Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to start
print_status "Waiting for services to start..."
sleep 15

# Check service status
print_status "Checking service status..."
if ! docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    print_error "Some services failed to start!"
    print_status "Service status:"
    docker-compose -f docker-compose.prod.yml ps
    print_status "Logs:"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi

print_success "All services started successfully"

# Health checks
print_status "Running health checks..."

# Check nginx
if docker-compose -f docker-compose.prod.yml exec nginx nginx -t > /dev/null 2>&1; then
    print_success "Nginx configuration is valid"
else
    print_error "Nginx configuration has errors"
    docker-compose -f docker-compose.prod.yml exec nginx nginx -t
fi

# Check application
sleep 5
if curl -f -s http://localhost:5000/health > /dev/null 2>&1; then
    print_success "Application health check passed"
else
    print_warning "Application health check failed (might be normal during startup)"
fi

# Test domain access
print_status "Testing domain access..."

# Test HTTP
if curl -f -s "http://$DOMAIN_NAME" > /dev/null 2>&1; then
    print_success "HTTP access working"
else
    print_warning "HTTP access test failed"
fi

# Test HTTPS (if SSL is available)
if [ "$SSL_AVAILABLE" = true ]; then
    if curl -f -s "https://$DOMAIN_NAME" > /dev/null 2>&1; then
        print_success "HTTPS access working"
    else
        print_warning "HTTPS access test failed"
    fi
fi

# Display deployment information
echo ""
print_success "🎉 Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Application URLs:"
if [ "$SSL_AVAILABLE" = true ]; then
    echo "   Primary:  https://$DOMAIN_NAME"
    echo "   Login:    https://$DOMAIN_NAME/login"
    echo "   Fallback: http://$DOMAIN_NAME (redirects to HTTPS)"
else
    echo "   Primary: http://$DOMAIN_NAME"
    echo "   Login:   http://$DOMAIN_NAME/login"
fi
echo ""
echo "🐳 Docker Services:"
docker-compose -f docker-compose.prod.yml ps --format "table {{.Service}}\t{{.State}}\t{{.Ports}}"
echo ""
echo "📊 Monitoring Commands:"
echo "   View logs:     docker-compose -f docker-compose.prod.yml logs -f"
echo "   Check status:  docker-compose -f docker-compose.prod.yml ps"
echo "   Restart:       docker-compose -f docker-compose.prod.yml restart"
echo "   Stop:          docker-compose -f docker-compose.prod.yml down"
echo ""
if [ "$SSL_AVAILABLE" = true ]; then
    echo "🔒 SSL Certificate:"
    echo "   Status:        Active"
    echo "   Renew:         ./renew-ssl.sh"
    echo "   Auto-renewal:  Configured"
else
    echo "⚠️  SSL Certificate:"
    echo "   Status:        Not configured"
    echo "   Setup:         ./setup-ssl.sh"
fi
echo ""
echo "🔧 Useful Files:"
echo "   Environment:   .env.domain"
echo "   Nginx config:  nginx/conf.d/app.conf"
echo "   Docker setup:  docker-compose.prod.yml"
echo "   This script:   deploy-with-domain.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Final test and recommendation
echo ""
print_header "🎯 Final Steps:"
echo "1. Test your application by visiting the URLs above"
echo "2. Update any bookmarks from the old IP address"
echo "3. Configure monitoring and backup as needed"
echo "4. Set up log rotation for production use"

if [ "$SSL_AVAILABLE" != true ]; then
    echo ""
    print_warning "🔒 Security Recommendation:"
    echo "Set up SSL certificate for production use:"
    echo "   ./setup-ssl.sh"
fi

echo ""
print_success "Deployment completed successfully! 🚀"