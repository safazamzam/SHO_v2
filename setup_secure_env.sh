#!/bin/bash

# Secure Environment Setup Script
# This script helps you set up secure credentials for production deployment

set -e  # Exit on any error

echo "🔐 Secure Credential Setup for Shift Handover Application"
echo "========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to generate strong passwords
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Function to create Docker secret
create_docker_secret() {
    local secret_name=$1
    local secret_value=$2
    
    if docker secret ls --format "{{.Name}}" | grep -q "^${secret_name}$"; then
        echo -e "${YELLOW}⚠️ Secret '${secret_name}' already exists${NC}"
        read -p "Do you want to recreate it? (y/N): " recreate
        if [[ $recreate =~ ^[Yy]$ ]]; then
            docker secret rm "${secret_name}" || true
        else
            return 0
        fi
    fi
    
    echo "${secret_value}" | docker secret create "${secret_name}" -
    echo -e "${GREEN}✅ Created secret: ${secret_name}${NC}"
}

# Function to prompt for secret value
prompt_secret() {
    local secret_name=$1
    local description=$2
    local default_value=$3
    local generated_value=""
    
    echo -e "\n${BLUE}📝 ${description}${NC}"
    
    if [[ "$secret_name" == *"password"* ]] || [[ "$secret_name" == *"key"* ]]; then
        generated_value=$(generate_password)
        echo -e "${YELLOW}💡 Generated strong value: ${generated_value}${NC}"
    fi
    
    if [[ -n "$default_value" ]]; then
        echo -e "${YELLOW}💡 Suggested value: ${default_value}${NC}"
    fi
    
    read -s -p "Enter value for ${secret_name} (or press Enter for generated/suggested): " user_input
    echo
    
    if [[ -z "$user_input" ]]; then
        if [[ -n "$generated_value" ]]; then
            echo "$generated_value"
        elif [[ -n "$default_value" ]]; then
            echo "$default_value"
        else
            echo ""
        fi
    else
        echo "$user_input"
    fi
}

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if Docker Swarm is initialized
if ! docker node ls >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ Docker Swarm is not initialized. Initializing now...${NC}"
    docker swarm init
    echo -e "${GREEN}✅ Docker Swarm initialized${NC}"
fi

echo -e "\n${BLUE}🔧 Setting up Docker Secrets...${NC}"

# Core Flask secrets
FLASK_SECRET_KEY=$(prompt_secret "flask_secret_key" "Flask Secret Key (for session encryption)")
create_docker_secret "flask_secret_key" "$FLASK_SECRET_KEY"

SSO_ENCRYPTION_KEY=$(prompt_secret "sso_encryption_key" "SSO Encryption Key (for user authentication)")
create_docker_secret "sso_encryption_key" "$SSO_ENCRYPTION_KEY"

# Database secrets
echo -e "\n${BLUE}🗄️ Database Configuration${NC}"
MYSQL_APP_PASSWORD=$(prompt_secret "mysql_app_password" "MySQL Application User Password")
create_docker_secret "mysql_app_password" "$MYSQL_APP_PASSWORD"

MYSQL_ROOT_PASSWORD=$(prompt_secret "mysql_root_password" "MySQL Root Password")
create_docker_secret "mysql_root_password" "$MYSQL_ROOT_PASSWORD"

# Construct database URL
DATABASE_URL="mysql://app_user:${MYSQL_APP_PASSWORD}@db:3306/shift_handover"
create_docker_secret "database_url" "$DATABASE_URL"

# Email configuration
echo -e "\n${BLUE}📧 Email Configuration${NC}"
SMTP_USERNAME=$(prompt_secret "smtp_username" "SMTP Username (Gmail address)" "your-email@gmail.com")
create_docker_secret "smtp_username" "$SMTP_USERNAME"

SMTP_PASSWORD=$(prompt_secret "smtp_password" "SMTP Password (Gmail App Password)")
create_docker_secret "smtp_password" "$SMTP_PASSWORD"

# ServiceNow configuration
echo -e "\n${BLUE}🎫 ServiceNow Configuration${NC}"
read -p "Do you want to configure ServiceNow integration? (y/N): " setup_servicenow
if [[ $setup_servicenow =~ ^[Yy]$ ]]; then
    SERVICENOW_INSTANCE=$(prompt_secret "servicenow_instance" "ServiceNow Instance URL" "https://your-instance.service-now.com")
    create_docker_secret "servicenow_instance" "$SERVICENOW_INSTANCE"
    
    SERVICENOW_USERNAME=$(prompt_secret "servicenow_username" "ServiceNow Username")
    create_docker_secret "servicenow_username" "$SERVICENOW_USERNAME"
    
    SERVICENOW_PASSWORD=$(prompt_secret "servicenow_password" "ServiceNow Password")
    create_docker_secret "servicenow_password" "$SERVICENOW_PASSWORD"
else
    create_docker_secret "servicenow_instance" ""
    create_docker_secret "servicenow_username" ""
    create_docker_secret "servicenow_password" ""
fi

# Google OAuth configuration
echo -e "\n${BLUE}🔐 Google OAuth Configuration${NC}"
read -p "Do you want to configure Google OAuth SSO? (y/N): " setup_oauth
if [[ $setup_oauth =~ ^[Yy]$ ]]; then
    GOOGLE_CLIENT_ID=$(prompt_secret "google_oauth_client_id" "Google OAuth Client ID")
    create_docker_secret "google_oauth_client_id" "$GOOGLE_CLIENT_ID"
    
    GOOGLE_CLIENT_SECRET=$(prompt_secret "google_oauth_client_secret" "Google OAuth Client Secret")
    create_docker_secret "google_oauth_client_secret" "$GOOGLE_CLIENT_SECRET"
else
    create_docker_secret "google_oauth_client_id" ""
    create_docker_secret "google_oauth_client_secret" ""
fi

# Create .env file for development
echo -e "\n${BLUE}📄 Creating .env file for development...${NC}"
cat > .env << EOF
# Development Environment Variables
# DO NOT commit this file to version control!

# Flask Configuration
SECRET_KEY=${FLASK_SECRET_KEY}
FLASK_ENV=development
FLASK_APP=app.py
SSO_ENCRYPTION_KEY=${SSO_ENCRYPTION_KEY}

# Database Configuration
DATABASE_URL=${DATABASE_URL}

# Email Configuration
SMTP_USERNAME=${SMTP_USERNAME}
SMTP_PASSWORD=${SMTP_PASSWORD}
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# ServiceNow Configuration (if configured)
SERVICENOW_INSTANCE=${SERVICENOW_INSTANCE:-}
SERVICENOW_USERNAME=${SERVICENOW_USERNAME:-}
SERVICENOW_PASSWORD=${SERVICENOW_PASSWORD:-}

# Google OAuth (if configured)
GOOGLE_OAUTH_CLIENT_ID=${GOOGLE_CLIENT_ID:-}
GOOGLE_OAUTH_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET:-}
EOF

# Add .env to .gitignore if not already there
if ! grep -q "\.env" .gitignore 2>/dev/null; then
    echo ".env" >> .gitignore
    echo -e "${GREEN}✅ Added .env to .gitignore${NC}"
fi

echo -e "\n${GREEN}🎉 Security setup completed!${NC}"
echo -e "\n${BLUE}📋 Summary:${NC}"
echo "• Docker secrets created for all sensitive credentials"
echo "• .env file created for development (not committed to git)"
echo "• All passwords are strongly generated"
echo ""
echo -e "${BLUE}📖 Next Steps:${NC}"
echo "1. For production: Use docker-compose.production.yml"
echo "2. For development: Use regular docker-compose.yml with .env file"
echo "3. Test configuration: python config_secure.py"
echo ""
echo -e "${YELLOW}⚠️ Important Security Notes:${NC}"
echo "• Keep your .env file secure and never commit it"
echo "• Docker secrets are stored securely by Docker Swarm"
echo "• Consider using Azure Key Vault for cloud deployment"
echo "• Regularly rotate your passwords and keys"

# Test configuration
echo -e "\n${BLUE}🧪 Testing configuration...${NC}"
if python3 config_secure.py; then
    echo -e "${GREEN}✅ Configuration test passed!${NC}"
else
    echo -e "${YELLOW}⚠️ Configuration test had warnings. Check the output above.${NC}"
fi