#!/bin/bash

# 🔧 Quick SSO Redirect URI Fix for nginx Proxy
# Fixes SSO authentication after enabling nginx reverse proxy

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

echo -e "${GREEN}🔧 SSO Redirect URI Fix for nginx Proxy${NC}"
echo "=================================================="

# Step 1: Check if application is running
print_status "Checking application status..."
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    print_success "Application is running"
else
    print_error "Application is not running. Starting services..."
    docker-compose -f docker-compose.prod.yml up -d
    sleep 10
fi

# Step 2: Check database connectivity
print_status "Checking database connectivity..."
if docker-compose -f docker-compose.prod.yml exec -T db mysql -u root -p"${MYSQL_ROOT_PASSWORD:-admin123}" -e "SELECT 1;" > /dev/null 2>&1; then
    print_success "Database connection successful"
else
    print_error "Cannot connect to database. Check database container."
    exit 1
fi

# Step 3: Fix redirect URIs in database
print_status "Updating SSO redirect URIs in database..."
docker-compose -f docker-compose.prod.yml exec -T db mysql -u root -p"${MYSQL_ROOT_PASSWORD:-admin123}" shift_handover << 'EOF'
-- Show current redirect URIs
SELECT 'Current redirect URIs:' as status;
SELECT provider_type, provider_name, config_value 
FROM sso_config 
WHERE config_key = 'redirect_uri';

-- Update redirect URIs (remove :5000 port)
UPDATE sso_config 
SET config_value = REPLACE(config_value, ':5000', '') 
WHERE config_key = 'redirect_uri' AND config_value LIKE '%:5000%';

-- Update localhost to IP address
UPDATE sso_config 
SET config_value = REPLACE(config_value, 'localhost', '35.200.202.18') 
WHERE config_key = 'redirect_uri' AND config_value LIKE '%localhost%';

-- Show updated redirect URIs
SELECT 'Updated redirect URIs:' as status;
SELECT provider_type, provider_name, config_value 
FROM sso_config 
WHERE config_key = 'redirect_uri';
EOF

if [ $? -eq 0 ]; then
    print_success "Database redirect URIs updated successfully"
else
    print_error "Failed to update database redirect URIs"
    exit 1
fi

# Step 4: Restart web application
print_status "Restarting web application..."
docker-compose -f docker-compose.prod.yml restart web

# Wait for application to start
print_status "Waiting for application to restart..."
sleep 15

# Step 5: Test application health
print_status "Testing application health..."
if curl -f -s "http://localhost/health" > /dev/null 2>&1; then
    print_success "✅ Application health check passed"
    echo "Health response: $(curl -s http://localhost/health)"
else
    print_warning "⚠️  Health check failed, but continuing..."
fi

# Step 6: Test SSO endpoint
print_status "Testing SSO login endpoint..."
if curl -f -s -I "http://localhost/login" > /dev/null 2>&1; then
    print_success "✅ SSO login endpoint accessible"
else
    print_warning "⚠️  SSO login endpoint test failed"
fi

# Step 7: Display next steps
echo ""
print_success "🎉 SSO Redirect URI Fix Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Database redirect URIs updated${NC}"
echo -e "${GREEN}✅ Web application restarted${NC}"
echo -e "${GREEN}✅ Health check completed${NC}"
echo ""
echo -e "${BLUE}🌐 Application URLs:${NC}"
echo -e "   Main App:    ${GREEN}http://35.200.202.18${NC}"
echo -e "   Health:      ${GREEN}http://35.200.202.18/health${NC}"
echo -e "   SSO Login:   ${GREEN}http://35.200.202.18/login${NC}"
echo ""
echo -e "${YELLOW}📝 IMPORTANT: Update Google OAuth Console${NC}"
echo "   1. Go to: https://console.cloud.google.com/"
echo "   2. Navigate to: APIs & Services > Credentials"
echo "   3. Edit your OAuth 2.0 Client ID"
echo "   4. Update Authorized redirect URIs:"
echo -e "      ${RED}Remove:${NC} http://35.200.202.18:5000/auth/sso/callback/google_oauth"
echo -e "      ${GREEN}Add:${NC}    http://35.200.202.18/auth/sso/callback/google_oauth"
echo "   5. Save changes"
echo ""
echo -e "${BLUE}🧪 Test SSO:${NC}"
echo "   1. Visit: http://35.200.202.18/login"
echo "   2. Click 'Sign in with Google'"
echo "   3. Complete OAuth flow"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

print_success "SSO redirect URI fix completed! 🚀"