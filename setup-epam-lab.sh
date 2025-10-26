#!/bin/bash

# 🏢 EPAM Lab Domain Setup Script for Linux
# Configures handover.lab.epam.com for Shift Handover App
# Target: 35.200.202.18 (Linux host)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Default values
DOMAIN="handover.lab.epam.com"
EMAIL=""
SKIP_SSL=false
TEST_MODE=false

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
    echo -e "${PURPLE}[EPAM-SETUP]${NC} $1"
}

# Function to show help
show_help() {
    echo -e "${PURPLE}🏢 EPAM Lab Domain Setup for Linux${NC}"
    echo "================================================"
    echo ""
    echo "This script configures handover.lab.epam.com domain access"
    echo ""
    echo "Usage:"
    echo "  ./setup-epam-lab.sh -e admin@epam.com"
    echo ""
    echo "Parameters:"
    echo "  -e, --email     Your EPAM email for SSL certificate (required)"
    echo "  -s, --skip-ssl  Skip SSL certificate setup (HTTP only)"
    echo "  -t, --test      Test configuration without applying changes"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Prerequisites:"
    echo "  1. Docker and Docker Compose installed"
    echo "  2. Domain handover.lab.epam.com pointing to this server (via NAT)"
    echo "  3. Ports 80 and 443 open in firewall"
    echo ""
    echo "Examples:"
    echo "  ./setup-epam-lab.sh -e admin@epam.com"
    echo "  ./setup-epam-lab.sh -e admin@epam.com --skip-ssl"
    echo "  ./setup-epam-lab.sh -e admin@epam.com --test"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--email)
            EMAIL="$2"
            shift 2
            ;;
        -s|--skip-ssl)
            SKIP_SSL=true
            shift
            ;;
        -t|--test)
            TEST_MODE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate required parameters
if [ -z "$EMAIL" ]; then
    print_error "Email is required! Use -e or --email parameter"
    echo ""
    show_help
    exit 1
fi

echo -e "${PURPLE}🏢 EPAM Lab Domain Setup${NC}"
echo "========================"
echo -e "${GREEN}Domain: $DOMAIN${NC}"
echo -e "${BLUE}Email:  $EMAIL${NC}"
if [ "$TEST_MODE" = true ]; then
    echo -e "${YELLOW}Mode:   TEST (no changes will be applied)${NC}"
fi
echo ""

# Check prerequisites
print_status "Checking prerequisites..."

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ] && ! groups $USER | grep -q '\bdocker\b'; then
    print_warning "You might need sudo privileges or be in the docker group"
    print_status "To add user to docker group: sudo usermod -aG docker \$USER"
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    print_status "Install Docker: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
    exit 1
fi

DOCKER_VERSION=$(docker --version)
print_success "Docker is available: $DOCKER_VERSION"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed or not in PATH"
    print_status "Install Docker Compose: sudo curl -L \"https://github.com/docker/compose/releases/download/1.29.2/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
    print_status "                        sudo chmod +x /usr/local/bin/docker-compose"
    exit 1
fi

COMPOSE_VERSION=$(docker-compose --version)
print_success "Docker Compose is available: $COMPOSE_VERSION"

# Step 1: Create EPAM Lab environment configuration
print_header "Creating EPAM Lab configuration..."

if [ "$TEST_MODE" = false ]; then
    cat > .env.domain << EOF
# 🌐 EPAM Lab Domain Setup Configuration
DOMAIN_NAME=$DOMAIN
EMAIL=$EMAIL
FLASK_ENV=production
FLASK_DEBUG=0
SSL_ENABLED=true
HTTP_PORT=80
HTTPS_PORT=443

# EPAM specific settings
ORGANIZATION=EPAM
ENVIRONMENT=lab
SERVICE_NAME=handover

# Network settings for NAT
EXTERNAL_IP=35.200.202.18
INTERNAL_PORT=5000

# Security settings
ENABLE_RATE_LIMITING=true
ENABLE_SECURITY_HEADERS=true
ENABLE_ACCESS_LOGS=true
EOF

    print_success "Created .env.domain with EPAM Lab settings"
else
    print_status "TEST MODE: Would create .env.domain configuration"
fi

# Step 2: Create EPAM Lab nginx configuration
print_header "Creating nginx configuration for $DOMAIN..."

if [ "$TEST_MODE" = false ]; then
    # Create nginx directories if they don't exist
    mkdir -p nginx/conf.d nginx/ssl

    cat > nginx/conf.d/app.conf << 'EOF'
# EPAM Lab Domain - Nginx Configuration for handover.lab.epam.com

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=general:10m rate=30r/m;

# Upstream to Flask app
upstream flask_app {
    server web:5000;
    keepalive 32;
}

# HTTP server - redirect to HTTPS
server {
    listen 80;
    server_name handover.lab.epam.com;
    
    # Let's Encrypt challenge location
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
        try_files $uri =404;
    }

    # Health check endpoint (for load balancer)
    location /health {
        proxy_pass http://flask_app/health;
        proxy_set_header Host $host;
        access_log off;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name handover.lab.epam.com;

    # SSL configuration - will be configured after certificate generation
    ssl_certificate /etc/letsencrypt/live/handover.lab.epam.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/handover.lab.epam.com/privkey.pem;
    
    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # EPAM Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self';" always;
    
    # EPAM custom header
    add_header X-Powered-By "EPAM-Labs" always;

    # Logging
    access_log /var/log/nginx/handover.lab.epam.com.access.log;
    error_log /var/log/nginx/handover.lab.epam.com.error.log;

    # Rate limiting for different endpoints
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }

    location /login {
        limit_req zone=login burst=5 nodelay;
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://flask_app/health;
        proxy_set_header Host $host;
        access_log off;
    }

    # Static files with caching
    location /static/ {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_cache_valid 200 1h;
        expires 1h;
        add_header Cache-Control "public, immutable";
    }

    # Main application with rate limiting
    location / {
        limit_req zone=general burst=50 nodelay;
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }
}
EOF

    print_success "Created nginx configuration for $DOMAIN"
else
    print_status "TEST MODE: Would create nginx configuration"
fi

# Step 3: Create necessary directories
print_status "Creating required directories..."
if [ "$TEST_MODE" = false ]; then
    mkdir -p certbot_conf certbot_www nginx/ssl logs
    print_success "Created directory structure"
else
    print_status "TEST MODE: Would create directories: certbot_conf, certbot_www, nginx/ssl, logs"
fi

# Step 4: DNS verification
print_header "Verifying DNS configuration..."

# Check if domain resolves
if command -v dig &> /dev/null; then
    DNS_RESULT=$(dig +short $DOMAIN)
    if [ -n "$DNS_RESULT" ]; then
        print_success "DNS resolved: $DOMAIN -> $DNS_RESULT"
    else
        print_warning "Could not resolve DNS for $DOMAIN"
        print_status "Make sure DNS is configured by the NAT team"
    fi
elif command -v nslookup &> /dev/null; then
    if nslookup $DOMAIN > /dev/null 2>&1; then
        print_success "DNS resolution appears to work for $DOMAIN"
    else
        print_warning "Could not resolve DNS for $DOMAIN"
    fi
else
    print_warning "No DNS lookup tools available (dig/nslookup)"
fi

# Step 5: Stop existing services
print_status "Stopping existing services..."
if [ "$TEST_MODE" = false ]; then
    docker-compose down > /dev/null 2>&1 || true
    docker-compose -f docker-compose.prod.yml down > /dev/null 2>&1 || true
    print_success "Stopped existing services"
else
    print_status "TEST MODE: Would stop existing Docker services"
fi

# Step 6: Start services for domain validation
print_header "Starting services for EPAM Lab domain..."
if [ "$TEST_MODE" = false ]; then
    # Start with production configuration
    if [ ! -f "docker-compose.prod.yml" ]; then
        print_error "docker-compose.prod.yml not found!"
        print_status "Please ensure you have the production Docker Compose file"
        exit 1
    fi
    
    # Start services
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services to start
    sleep 10
    
    # Check if services are running
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        print_success "Services started successfully"
        
        # Show service status
        echo ""
        print_status "Service Status:"
        docker-compose -f docker-compose.prod.yml ps
    else
        print_warning "Some services may have issues. Check logs:"
        print_status "docker-compose -f docker-compose.prod.yml logs"
    fi
else
    print_status "TEST MODE: Would start Docker services with docker-compose.prod.yml"
fi

# Step 7: SSL Certificate setup (if not skipped)
if [ "$SKIP_SSL" = false ]; then
    print_header "Setting up SSL certificate for $DOMAIN..."
    
    if [ "$TEST_MODE" = false ]; then
        # Wait a bit more for nginx to be ready
        sleep 5
        
        # Test HTTP access first
        print_status "Testing HTTP access for domain validation..."
        
        # Try to get SSL certificate
        print_status "Obtaining SSL certificate from Let's Encrypt..."
        
        if docker run --rm \
            -v "$(pwd)/certbot_conf:/etc/letsencrypt" \
            -v "$(pwd)/certbot_www:/var/www/certbot" \
            certbot/certbot certonly \
            --webroot \
            --webroot-path=/var/www/certbot \
            --email "$EMAIL" \
            --agree-tos \
            --no-eff-email \
            --non-interactive \
            -d "$DOMAIN"; then
            
            if [ -f "certbot_conf/live/$DOMAIN/fullchain.pem" ]; then
                print_success "SSL certificate obtained successfully!"
                
                # Restart services with SSL
                print_status "Restarting services with SSL configuration..."
                docker-compose -f docker-compose.prod.yml restart
                sleep 10
                
                print_success "Services restarted with SSL support"
            else
                print_warning "SSL certificate files not found after generation"
            fi
        else
            print_warning "SSL certificate generation failed"
            print_status "Continuing with HTTP-only setup"
            print_status "You can retry SSL setup later with:"
            echo "  docker run --rm -v \$(pwd)/certbot_conf:/etc/letsencrypt -v \$(pwd)/certbot_www:/var/www/certbot certbot/certbot certonly --webroot --webroot-path=/var/www/certbot --email $EMAIL --agree-tos --no-eff-email -d $DOMAIN"
        fi
    else
        print_status "TEST MODE: Would obtain SSL certificate for $DOMAIN"
    fi
else
    print_status "Skipping SSL setup as requested"
fi

# Step 8: Health checks and testing
print_header "Running health checks..."

if [ "$TEST_MODE" = false ]; then
    # Test HTTP access
    print_status "Testing HTTP access..."
    if curl -f -s "http://$DOMAIN/health" > /dev/null 2>&1; then
        print_success "HTTP health check passed"
    else
        print_warning "HTTP health check failed - this might be normal if NAT isn't configured yet"
        print_status "Testing local access..."
        if curl -f -s "http://localhost:80/health" > /dev/null 2>&1; then
            print_success "Local HTTP access works - issue might be with NAT/DNS"
        fi
    fi
    
    # Test HTTPS access (if SSL was set up)
    if [ "$SKIP_SSL" = false ] && [ -f "certbot_conf/live/$DOMAIN/fullchain.pem" ]; then
        print_status "Testing HTTPS access..."
        if curl -f -s "https://$DOMAIN/health" > /dev/null 2>&1; then
            print_success "HTTPS health check passed"
        else
            print_warning "HTTPS health check failed - certificate might need time to propagate"
        fi
    fi
else
    print_status "TEST MODE: Would run health checks"
fi

# Step 9: Create monitoring and maintenance scripts
print_header "Creating monitoring scripts..."

if [ "$TEST_MODE" = false ]; then
    # Create monitoring script
    cat > monitor-epam-lab.sh << 'EOF'
#!/bin/bash

# 🏢 EPAM Lab - Monitoring Script for Shift Handover App

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🏢 EPAM Lab Handover App - Monitor${NC}"
echo "===================================="

echo -e "\n${BLUE}📊 Service Status:${NC}"
docker-compose -f docker-compose.prod.yml ps

echo -e "\n${BLUE}📋 Recent Application Logs:${NC}"
docker-compose -f docker-compose.prod.yml logs --tail=50 web

echo -e "\n${BLUE}🌐 Recent Nginx Logs:${NC}"
docker-compose -f docker-compose.prod.yml logs --tail=20 nginx

echo -e "\n${BLUE}🔍 Quick Health Check:${NC}"
if curl -f -s https://handover.lab.epam.com/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Application is healthy${NC}"
else
    echo -e "${RED}❌ Application health check failed${NC}"
    echo "Testing local access..."
    if curl -f -s http://localhost:80/health > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Local access works - check NAT/DNS configuration${NC}"
    else
        echo -e "${RED}❌ Local access also failed${NC}"
    fi
fi

echo -e "\n${BLUE}💾 Disk Usage:${NC}"
df -h | grep -E "(Size|/dev/)"

echo -e "\n${BLUE}🐳 Docker System:${NC}"
docker system df

echo -e "\n${BLUE}📈 Memory Usage:${NC}"
free -h
EOF

    chmod +x monitor-epam-lab.sh
    print_success "Created monitoring script: monitor-epam-lab.sh"
    
    # Create SSL renewal script
    cat > renew-ssl.sh << EOF
#!/bin/bash

# SSL Certificate Renewal for EPAM Lab
echo "🔒 Renewing SSL certificates for handover.lab.epam.com..."

docker run --rm \\
    -v "\$(pwd)/certbot_conf:/etc/letsencrypt" \\
    -v "\$(pwd)/certbot_www:/var/www/certbot" \\
    certbot/certbot renew --quiet

if [ \$? -eq 0 ]; then
    echo "✅ Certificate renewed successfully. Restarting nginx..."
    docker-compose -f docker-compose.prod.yml restart nginx
    echo "✅ Nginx restarted."
else
    echo "❌ Certificate renewal failed!"
fi
EOF

    chmod +x renew-ssl.sh
    print_success "Created SSL renewal script: renew-ssl.sh"
else
    print_status "TEST MODE: Would create monitoring and maintenance scripts"
fi

# Final results
echo ""
print_success "🎉 EPAM Lab Domain Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$TEST_MODE" = false ]; then
    echo -e "${BLUE}🌐 EPAM Lab Application URLs:${NC}"
    if [ "$SKIP_SSL" = false ] && [ -f "certbot_conf/live/$DOMAIN/fullchain.pem" ]; then
        echo -e "   ${GREEN}Primary:  https://$DOMAIN${NC}"
        echo -e "   ${GREEN}Login:    https://$DOMAIN/login${NC}"
        echo -e "   ${GREEN}Health:   https://$DOMAIN/health${NC}"
    else
        echo -e "   ${YELLOW}Primary: http://$DOMAIN${NC}"
        echo -e "   ${YELLOW}Login:   http://$DOMAIN/login${NC}"
        echo -e "   ${YELLOW}Health:  http://$DOMAIN/health${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}🔧 Management Commands:${NC}"
    echo "   Monitor:       ./monitor-epam-lab.sh"
    echo "   Check status:  docker-compose -f docker-compose.prod.yml ps"
    echo "   View logs:     docker-compose -f docker-compose.prod.yml logs -f"
    echo "   Restart:       docker-compose -f docker-compose.prod.yml restart"
    
    if [ "$SKIP_SSL" = false ]; then
        echo "   Renew SSL:     ./renew-ssl.sh"
    fi
    
    echo ""
    echo -e "${PURPLE}🏢 EPAM Lab Configuration:${NC}"
    echo "   Domain:        $DOMAIN"
    echo "   Environment:   Production (EPAM Lab)"
    if [ "$SKIP_SSL" = false ] && [ -f "certbot_conf/live/$DOMAIN/fullchain.pem" ]; then
        echo "   SSL:           Enabled"
    else
        echo "   SSL:           Disabled"
    fi
    echo "   Rate Limiting: Enabled"
    echo "   Access Logs:   Enabled"
    
    echo ""
    echo -e "${YELLOW}📋 Next Steps:${NC}"
    echo "1. Test your application: curl https://$DOMAIN/health"
    echo "2. Ensure NAT team has configured forwarding to this server"
    echo "3. Monitor logs: ./monitor-epam-lab.sh"
    echo "4. Set up regular backups and monitoring"
else
    echo -e "${YELLOW}This was a test run. To apply changes, run without --test${NC}"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_success "Setup completed successfully! 🚀"

if [ "$TEST_MODE" = false ]; then
    echo ""
    echo -e "${GREEN}Your Shift Handover App is now available at $DOMAIN${NC}"
    echo -e "${BLUE}Make sure the NAT team forwards traffic to this server (35.200.202.18)${NC}"
fi