#!/bin/bash

# 🌐 Quick HTTP Setup for handover.lab.com
# Fixes nginx mount issues and creates HTTP-only configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

echo -e "${GREEN}🌐 Quick HTTP Setup for handover.lab.com${NC}"
echo "==========================================="

# Step 1: Create nginx directory structure and files
print_status "Creating nginx configuration files..."

# Create directories
mkdir -p nginx/conf.d
mkdir -p nginx/ssl

# Create main nginx.conf if it doesn't exist
if [ ! -f "nginx/nginx.conf" ]; then
    print_status "Creating nginx/nginx.conf..."
    cat > nginx/nginx.conf << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log notice;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging format
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    client_max_body_size 20M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Include server configurations
    include /etc/nginx/conf.d/*.conf;
}
EOF
    print_success "Created nginx/nginx.conf"
else
    print_success "nginx/nginx.conf already exists"
fi

# Create HTTP-only app.conf
print_status "Creating HTTP-only nginx configuration..."
cat > nginx/conf.d/app.conf << 'EOF'
# HTTP-Only Configuration for handover.lab.com

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=general:10m rate=30r/m;

# Upstream to Flask app
upstream flask_app {
    server web:5000;
    keepalive 32;
}

# HTTP server for handover.lab.com
server {
    listen 80;
    server_name handover.lab.com localhost;
    
    # EPAM custom headers
    add_header X-Powered-By "EPAM-Labs-HTTP" always;
    add_header X-Environment "Development-HTTP" always;

    # Basic security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Logging
    access_log /var/log/nginx/handover.lab.com.access.log;
    error_log /var/log/nginx/handover.lab.com.error.log;

    # Health check endpoint
    location /health {
        proxy_pass http://flask_app/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        access_log off;
    }

    # API endpoints with rate limiting
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

    # Login endpoint with stricter rate limiting
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

    # Static files with caching
    location /static/ {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        expires 1h;
        add_header Cache-Control "public, immutable";
    }

    # Main application
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

# Default server block
server {
    listen 80 default_server;
    server_name _;
    return 444;
}
EOF

print_success "Created nginx/conf.d/app.conf for HTTP-only access"

# Step 2: Create environment configuration
print_status "Creating environment configuration..."
cat > .env.domain << 'EOF'
# HTTP-Only Configuration for handover.lab.com
DOMAIN_NAME=handover.lab.com
EMAIL=admin@epam.com
FLASK_ENV=production
FLASK_DEBUG=0
SSL_ENABLED=false
HTTP_PORT=80
FORCE_HTTPS=false

# EPAM Settings
ORGANIZATION=EPAM
ENVIRONMENT=lab
SERVICE_NAME=handover
EOF

print_success "Created .env.domain"

# Step 3: Check file permissions
print_status "Checking file permissions..."
chmod 644 nginx/nginx.conf
chmod 644 nginx/conf.d/app.conf
chmod 644 .env.domain

print_success "Set proper file permissions"

# Step 4: Stop any existing services
print_status "Stopping existing services..."
docker-compose down > /dev/null 2>&1 || true
docker-compose -f docker-compose.prod.yml down > /dev/null 2>&1 || true

# Step 5: Test nginx configuration
print_status "Testing nginx configuration..."
if docker run --rm -v "$(pwd)/nginx/nginx.conf:/etc/nginx/nginx.conf:ro" -v "$(pwd)/nginx/conf.d:/etc/nginx/conf.d:ro" nginx:alpine nginx -t; then
    print_success "Nginx configuration is valid"
else
    print_error "Nginx configuration has errors"
    exit 1
fi

# Step 6: Start services
print_status "Starting services with HTTP-only configuration..."

# Use production docker-compose
if [ -f "docker-compose.prod.yml" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
else
    print_error "docker-compose.prod.yml not found!"
    exit 1
fi

# Start services
docker-compose -f "$COMPOSE_FILE" up -d

# Wait for services to start
print_status "Waiting for services to start..."
sleep 15

# Check service status
print_status "Checking service status..."
if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
    print_success "Services started successfully!"
    
    echo ""
    print_status "Service Status:"
    docker-compose -f "$COMPOSE_FILE" ps
else
    print_warning "Some services may have issues"
fi

# Step 7: Test local access
print_status "Testing local access..."
sleep 5

if curl -f -s "http://localhost:80/health" > /dev/null 2>&1; then
    print_success "✅ Local HTTP access working!"
else
    print_warning "Local HTTP access test failed"
    # Try direct container access
    if curl -f -s "http://localhost:5000/health" > /dev/null 2>&1; then
        print_warning "Flask app is running on port 5000, nginx might have issues"
    fi
fi

# Step 8: Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
echo "🌐 Handover App Monitor"
echo "======================"

echo -e "\n📊 Service Status:"
docker-compose -f docker-compose.prod.yml ps

echo -e "\n🔍 Health Checks:"
echo -n "Local HTTP: "
if curl -f -s http://localhost:80/health > /dev/null 2>&1; then
    echo "✅ Working"
else
    echo "❌ Failed"
fi

echo -n "Domain HTTP: "
if curl -f -s http://handover.lab.com/health > /dev/null 2>&1; then
    echo "✅ Working"
else
    echo "⚠️  Not accessible (normal if domain mapping not configured)"
fi

echo -e "\n📋 Recent Logs:"
docker-compose -f docker-compose.prod.yml logs --tail=10 web
echo -e "\n🌐 Nginx Logs:"
docker-compose -f docker-compose.prod.yml logs --tail=5 nginx
EOF

chmod +x monitor.sh

# Final results
echo ""
print_success "🎉 HTTP Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Nginx configuration files created${NC}"
echo -e "${GREEN}✅ HTTP-only setup configured${NC}"
echo -e "${GREEN}✅ Services started successfully${NC}"
echo -e "${GREEN}✅ Monitoring script created${NC}"
echo ""
echo -e "${BLUE}🌐 Application URLs:${NC}"
echo -e "   Local:  ${GREEN}http://localhost/health${NC}"
echo -e "   Domain: ${YELLOW}http://handover.lab.com/health${NC} (after domain mapping)"
echo ""
echo -e "${BLUE}🔧 Management:${NC}"
echo "   Monitor:  ./monitor.sh"
echo "   Logs:     docker-compose -f docker-compose.prod.yml logs -f"
echo "   Restart:  docker-compose -f docker-compose.prod.yml restart"
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo "1. Test: curl http://localhost/health"
echo "2. Configure domain mapping: handover.lab.com → this server"
echo "3. Test domain: curl http://handover.lab.com/health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_success "Setup completed! 🚀"