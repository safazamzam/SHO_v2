#!/bin/bash
# Setup Docker Secrets for Shift Handover App
# Run this script to create all required Docker secrets

echo "Setting up Docker Secrets for Shift Handover App"
echo "=================================================="

# Function to create secret
create_secret() {
    local name=$1
    local description=$2
    local value=$3
    
    if [ -z "$value" ]; then
        echo -n "Enter $description: "
        read -s value
        echo
    fi
    
    echo "$value" | docker secret create "$name" - 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "Created secret: $name"
    else
        echo "Secret $name already exists or failed to create"
    fi
}

# Database secrets
echo ""
echo "Database Secrets"
create_secret "shift_handover_mysql_password" "MySQL app user password"
create_secret "shift_handover_mysql_root_password" "MySQL root password"

# Generate database URL
echo -n "Enter database host (default: db): "
read db_host
db_host=${db_host:-db}

echo -n "Enter database name (default: shift_handover): "
read db_name
db_name=${db_name:-shift_handover}

echo -n "Enter database username (default: app_user): "
read db_user
db_user=${db_user:-app_user}

# Get the MySQL password (you'll need to enter this again)
echo -n "Re-enter MySQL app user password for DATABASE_URL: "
read -s mysql_pass
echo

database_url="mysql+pymysql://$db_user:$mysql_pass@$db_host:3306/$db_name"
create_secret "shift_handover_database_url" "Database connection URL" "$database_url"

# Application secrets
echo ""
echo "Application Secrets"
secrets_key="tSo-GG44Oa9MGWQmXv470mdCPxMRwhuejU87skv22ZQ="
create_secret "shift_handover_secrets_master_key" "Secrets master key" "$secrets_key"

echo ""
echo "All secrets created successfully!"
echo ""
echo "Next steps:"
echo "1. Deploy with: docker-compose -f docker-compose.production-secrets.yml up -d"
echo "2. Check logs: docker-compose -f docker-compose.production-secrets.yml logs"
echo "3. Access app: http://localhost:5000"
echo ""
echo "Access secrets dashboard:"
echo "- URL: http://localhost:5000/admin/secrets/"
echo "- Login: admin / admin123"
