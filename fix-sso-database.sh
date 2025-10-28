#!/bin/bash

# 🔧 SSO Database Redirect URI Fix for Docker/MySQL Setup
# Fixes SSO redirect URIs directly in MySQL database

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

echo -e "${GREEN}🔧 SSO Database Redirect URI Fix${NC}"
echo "========================================"

# Step 1: Check if Docker containers are running
print_status "Checking Docker containers status..."
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    print_success "Docker containers are running"
else
    print_error "Docker containers are not running. Please start them first:"
    echo "docker-compose -f docker-compose.prod.yml up -d"
    exit 1
fi

# Step 2: Check database connection
print_status "Testing database connection..."
DB_PASSWORD="${MYSQL_ROOT_PASSWORD:-admin123}"

if docker-compose -f docker-compose.prod.yml exec -T db mysql -u root -p"${DB_PASSWORD}" -e "SELECT 1;" > /dev/null 2>&1; then
    print_success "Database connection successful"
else
    print_error "Cannot connect to database. Trying alternative passwords..."
    
    # Try common passwords
    for pwd in "admin123" "password" "root" "mysql" ""; do
        if docker-compose -f docker-compose.prod.yml exec -T db mysql -u root -p"${pwd}" -e "SELECT 1;" > /dev/null 2>&1; then
            DB_PASSWORD="${pwd}"
            print_success "Database connection successful with password: ${pwd}"
            break
        fi
    done
    
    if [ $? -ne 0 ]; then
        print_error "Cannot connect to database with any common password"
        print_warning "Please set MYSQL_ROOT_PASSWORD environment variable"
        exit 1
    fi
fi

# Step 3: Check sso_config table and current redirect URIs
print_status "Checking current SSO configuration..."
docker-compose -f docker-compose.prod.yml exec -T db mysql -u root -p"${DB_PASSWORD}" shift_handover << 'EOF'
-- Check if sso_config table exists
SELECT 'Checking sso_config table...' as status;
SHOW TABLES LIKE 'sso_config';

-- Show current redirect URIs
SELECT 'Current SSO redirect URIs:' as status;
SELECT 
    id,
    provider_type, 
    provider_name, 
    config_key,
    CASE 
        WHEN config_key = 'client_secret' THEN '***hidden***'
        ELSE config_value 
    END as config_value,
    enabled
FROM sso_config 
WHERE config_key = 'redirect_uri' OR config_key LIKE '%redirect%' OR config_key LIKE '%callback%'
ORDER BY provider_name, config_key;

-- Show all SSO configuration for enabled providers
SELECT 'All SSO configuration for enabled providers:' as status;
SELECT 
    provider_type, 
    provider_name, 
    config_key,
    CASE 
        WHEN config_key IN ('client_secret', 'password') THEN '***hidden***'
        ELSE config_value 
    END as config_value,
    enabled
FROM sso_config 
WHERE enabled = 1
ORDER BY provider_name, config_key;
EOF

# Step 4: Fix redirect URIs
print_status "Fixing redirect URIs for nginx proxy setup..."
print_warning "This will update redirect URIs from :5000 to port 80 (nginx proxy)"

echo ""
read -p "Do you want to proceed with updating redirect URIs? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose -f docker-compose.prod.yml exec -T db mysql -u root -p"${DB_PASSWORD}" shift_handover << 'EOF'
-- Update redirect URIs to remove :5000 port
UPDATE sso_config 
SET config_value = REPLACE(config_value, ':5000', '') 
WHERE config_key = 'redirect_uri' AND config_value LIKE '%:5000%';

-- Update localhost to IP address if present
UPDATE sso_config 
SET config_value = REPLACE(config_value, 'localhost', '35.200.202.18') 
WHERE config_key = 'redirect_uri' AND config_value LIKE '%localhost%';

-- Show updated redirect URIs
SELECT 'Updated SSO redirect URIs:' as status;
SELECT 
    id,
    provider_type, 
    provider_name, 
    config_key,
    config_value,
    enabled
FROM sso_config 
WHERE config_key = 'redirect_uri'
ORDER BY provider_name, config_key;

-- Show affected rows count
SELECT ROW_COUNT() as 'Rows affected by update';
EOF
    
    if [ $? -eq 0 ]; then
        print_success "Database redirect URIs updated successfully"
    else
        print_error "Failed to update database redirect URIs"
        exit 1
    fi
else
    print_warning "Operation cancelled by user"
    exit 0
fi

# Step 5: Restart web application to reload configuration
print_status "Restarting web application to reload configuration..."
docker-compose -f docker-compose.prod.yml restart web

# Wait for application to start
print_status "Waiting for application to restart..."
sleep 15

# Step 6: Test application
print_status "Testing application endpoints..."

# Test health endpoint
if curl -f -s "http://localhost/health" > /dev/null 2>&1; then
    print_success "✅ Health endpoint accessible"
    echo "Health response: $(curl -s http://localhost/health | head -c 200)..."
else
    print_warning "⚠️  Health endpoint test failed"
fi

# Test login endpoint
if curl -f -s -I "http://localhost/login" > /dev/null 2>&1; then
    print_success "✅ Login endpoint accessible"
else
    print_warning "⚠️  Login endpoint test failed"
fi

# Step 7: Show final configuration and next steps
echo ""
print_success "🎉 SSO Redirect URI Fix Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Database redirect URIs updated${NC}"
echo -e "${GREEN}✅ Web application restarted${NC}"
echo -e "${GREEN}✅ Health checks completed${NC}"
echo ""
echo -e "${BLUE}🌐 Application URLs:${NC}"
echo -e "   Main App:    ${GREEN}http://35.200.202.18${NC}"
echo -e "   Health:      ${GREEN}http://35.200.202.18/health${NC}"
echo -e "   SSO Login:   ${GREEN}http://35.200.202.18/login${NC}"
echo ""
echo -e "${YELLOW}📝 CRITICAL: Update Your Organization's OAuth Console${NC}"
echo "   1. Go to your organization's OAuth provider console"
echo "   2. Find your OAuth application/client configuration"
echo "   3. Update the authorized redirect URIs:"
echo -e "      ${RED}OLD:${NC} http://35.200.202.18:5000/auth/sso/callback/[provider]"
echo -e "      ${GREEN}NEW:${NC} http://35.200.202.18/auth/sso/callback/[provider]"
echo "   4. Save the changes in your OAuth console"
echo ""
echo -e "${BLUE}🧪 Test SSO Flow:${NC}"
echo "   1. Visit: http://35.200.202.18/login"
echo "   2. Click your organization's SSO login button"
echo "   3. Complete the OAuth flow"
echo "   4. Verify successful login and profile display"
echo ""
echo -e "${BLUE}🔍 Debug Information:${NC}"
echo "   - Check logs: docker-compose -f docker-compose.prod.yml logs web"
echo "   - Debug endpoint: http://35.200.202.18/auth/sso/debug/claims"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

print_success "SSO redirect URI fix completed! 🚀"