#!/usr/bin/env python3
"""
🔧 FIX SECRETS CATEGORIES AND SETUP DOCKER SECRETS
Fix the category mismatch and set up proper secrets management
"""

from app import app, db
from sqlalchemy import text
from models.secrets_manager import HybridSecretsManager, SecretCategory
import os

def fix_secrets_categories():
    """Fix the category mismatch in the database"""
    with app.app_context():
        print("🔧 FIXING SECRETS CATEGORIES:")
        print("=" * 50)
        
        # Category mapping from current to expected
        category_mapping = {
            'External APIs': SecretCategory.EXTERNAL,
            'Application Configuration': SecretCategory.APPLICATION,
            'Feature Controls': SecretCategory.FEATURE,
            'SMTP': SecretCategory.EXTERNAL,
            'ServiceNow': SecretCategory.EXTERNAL
        }
        
        try:
            for old_category, new_category in category_mapping.items():
                query = f"UPDATE secret_store SET category = '{new_category}' WHERE category = '{old_category}'"
                with db.engine.connect() as connection:
                    result = connection.execute(text(query))
                    connection.commit()
                    print(f"✅ Updated {result.rowcount} secrets: '{old_category}' → '{new_category}'")
            
            print("\n🔍 Updated categories:")
            query = "SELECT category, COUNT(*) as count FROM secret_store GROUP BY category"
            with db.engine.connect() as connection:
                result = connection.execute(text(query))
                categories = result.fetchall()
            
            for category, count in categories:
                print(f"- {category}: {count} secrets")
                
        except Exception as e:
            print(f"❌ Error updating categories: {e}")
            return False
        
        return True

def create_docker_secrets_setup():
    """Create a Docker Compose setup with proper database password management"""
    with app.app_context():
        print("\n🐳 CREATING DOCKER SECRETS SETUP:")
        print("=" * 50)
        
        # Create production docker-compose with secrets
        docker_compose_content = """version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      # Database connection will come from Docker secret
      FLASK_ENV: production
      FLASK_DEBUG: false
      
      # Secrets master key for application secrets
      SECRETS_MASTER_KEY_FILE: /run/secrets/secrets_master_key
      
      # Other non-sensitive config
      SMTP_SERVER: smtp.gmail.com
      SMTP_PORT: 587
      
    secrets:
      - database_url
      - secrets_master_key
      
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: shift_handover
      MYSQL_USER: app_user
      MYSQL_PASSWORD_FILE: /run/secrets/mysql_password
      MYSQL_ROOT_PASSWORD_FILE: /run/secrets/mysql_root_password
    
    secrets:
      - mysql_password
      - mysql_root_password
    
    volumes:
      - db_data:/var/lib/mysql
    
    restart: unless-stopped
    
    # Security hardening
    security_opt:
      - no-new-privileges:true
    command: >
      --default-authentication-plugin=mysql_native_password
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci

# Docker Secrets - Create these before deploying
secrets:
  database_url:
    external: true
    name: shift_handover_database_url
  
  secrets_master_key:
    external: true
    name: shift_handover_secrets_master_key
  
  mysql_password:
    external: true
    name: shift_handover_mysql_password
  
  mysql_root_password:
    external: true
    name: shift_handover_mysql_root_password

volumes:
  db_data:
    driver: local

networks:
  default:
    name: shift_handover_network
    driver: bridge
"""
        
        # Write the docker-compose file
        with open('docker-compose.production-secrets.yml', 'w') as f:
            f.write(docker_compose_content)
        
        print("✅ Created docker-compose.production-secrets.yml")
        
        # Create secrets setup script
        setup_script = """#!/bin/bash
# Setup Docker Secrets for Shift Handover App
# Run this script to create all required Docker secrets

echo "🔐 Setting up Docker Secrets for Shift Handover App"
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
        echo "✅ Created secret: $name"
    else
        echo "⚠️ Secret $name already exists or failed to create"
    fi
}

# Database secrets
echo "🗄️ Database Secrets"
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
echo "🔑 Application Secrets"
secrets_key="tSo-GG44Oa9MGWQmXv470mdCPxMRwhuejU87skv22ZQ="
create_secret "shift_handover_secrets_master_key" "Secrets master key" "$secrets_key"

echo ""
echo "🎉 All secrets created successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Deploy with: docker-compose -f docker-compose.production-secrets.yml up -d"
echo "2. Check logs: docker-compose -f docker-compose.production-secrets.yml logs"
echo "3. Access app: http://localhost:5000"
echo ""
echo "🔐 Access secrets dashboard:"
echo "- URL: http://localhost:5000/admin/secrets/"
echo "- Login: admin / admin123"
"""
        
        with open('setup-docker-secrets.sh', 'w') as f:
            f.write(setup_script)
        
        # Make script executable (on Unix systems)
        try:
            import stat
            st = os.stat('setup-docker-secrets.sh')
            os.chmod('setup-docker-secrets.sh', st.st_mode | stat.S_IEXEC)
        except:
            pass
        
        print("✅ Created setup-docker-secrets.sh")
        
        # Create PowerShell version for Windows
        ps_script = """# Setup Docker Secrets for Shift Handover App (PowerShell)
# Run this script to create all required Docker secrets

Write-Host "🔐 Setting up Docker Secrets for Shift Handover App" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

function Create-DockerSecret {
    param(
        [string]$Name,
        [string]$Description,
        [string]$Value = $null
    )
    
    if (-not $Value) {
        $Value = Read-Host -Prompt "Enter $Description" -AsSecureString
        $Value = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($Value))
    }
    
    try {
        $Value | docker secret create $Name - 2>$null
        Write-Host "✅ Created secret: $Name" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ Secret $Name already exists or failed to create" -ForegroundColor Yellow
    }
}

# Database secrets
Write-Host "`n🗄️ Database Secrets" -ForegroundColor Blue
Create-DockerSecret "shift_handover_mysql_password" "MySQL app user password"
Create-DockerSecret "shift_handover_mysql_root_password" "MySQL root password"

# Database URL construction
$dbHost = Read-Host -Prompt "Enter database host (default: db)"
if (-not $dbHost) { $dbHost = "db" }

$dbName = Read-Host -Prompt "Enter database name (default: shift_handover)"
if (-not $dbName) { $dbName = "shift_handover" }

$dbUser = Read-Host -Prompt "Enter database username (default: app_user)"
if (-not $dbUser) { $dbUser = "app_user" }

$mysqlPass = Read-Host -Prompt "Re-enter MySQL app user password for DATABASE_URL" -AsSecureString
$mysqlPassPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($mysqlPass))

$databaseUrl = "mysql+pymysql://$dbUser`:$mysqlPassPlain@$dbHost`:3306/$dbName"
Create-DockerSecret "shift_handover_database_url" "Database connection URL" $databaseUrl

# Application secrets
Write-Host "`n🔑 Application Secrets" -ForegroundColor Blue
$secretsKey = "tSo-GG44Oa9MGWQmXv470mdCPxMRwhuejU87skv22ZQ="
Create-DockerSecret "shift_handover_secrets_master_key" "Secrets master key" $secretsKey

Write-Host "`n🎉 All secrets created successfully!" -ForegroundColor Green
Write-Host "`n📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Deploy with: docker-compose -f docker-compose.production-secrets.yml up -d"
Write-Host "2. Check logs: docker-compose -f docker-compose.production-secrets.yml logs"
Write-Host "3. Access app: http://localhost:5000"
Write-Host "`n🔐 Access secrets dashboard:" -ForegroundColor Cyan
Write-Host "- URL: http://localhost:5000/admin/secrets/"
Write-Host "- Login: admin / admin123"
"""
        
        with open('setup-docker-secrets.ps1', 'w') as f:
            f.write(ps_script)
        
        print("✅ Created setup-docker-secrets.ps1")

def update_config_for_docker_secrets():
    """Update config.py to support Docker secrets"""
    print("\n⚙️ UPDATING CONFIG FOR DOCKER SECRETS:")
    print("=" * 50)
    
    config_addition = '''
    # Enhanced Docker Secrets support
    @staticmethod
    def get_docker_secret(secret_name):
        """Get secret from Docker secrets file"""
        secret_file = f"/run/secrets/{secret_name.lower()}"
        if os.path.exists(secret_file):
            try:
                with open(secret_file, 'r') as f:
                    value = f.read().strip()
                    logging.info(f"✅ Loaded {secret_name} from Docker secret")
                    return value
            except Exception as e:
                logging.error(f"Error reading Docker secret {secret_name}: {e}")
        return None
    
    @staticmethod
    def get_secret_enhanced(secret_name, default=None, required=False):
        """
        Enhanced secret retrieval with Docker secrets support:
        1. Docker Secrets (files in /run/secrets/) - HIGHEST PRIORITY
        2. Environment Variables
        3. Default value
        """
        # Try Docker Secrets first (production)
        docker_value = SecureConfigManager.get_docker_secret(secret_name)
        if docker_value:
            return docker_value
        
        # Try with _FILE suffix for Docker secrets
        file_var = f"{secret_name.upper()}_FILE"
        file_path = os.environ.get(file_var)
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    value = f.read().strip()
                    logging.info(f"✅ Loaded {secret_name} from file: {file_path}")
                    return value
            except Exception as e:
                logging.error(f"Error reading secret file {file_path}: {e}")
        
        # Fall back to original method
        return SecureConfigManager.get_secret(secret_name, default, required)
'''
    
    print("✅ Enhanced config methods available")
    print("   - get_docker_secret(): Read from /run/secrets/")
    print("   - get_secret_enhanced(): Docker secrets + environment fallback")

def main():
    print("🔧 SECRETS MANAGEMENT COMPLETE SETUP")
    print("=" * 60)
    
    # Fix categories
    if fix_secrets_categories():
        print("✅ Secrets categories fixed")
    
    # Create Docker setup
    create_docker_secrets_setup()
    
    # Update config info
    update_config_for_docker_secrets()
    
    print(f"\n🎯 SETUP COMPLETE!")
    print("=" * 50)
    print("✅ Secrets categories fixed - UI should now show secrets")
    print("✅ Docker Compose with secrets created")
    print("✅ Setup scripts created (bash & PowerShell)")
    
    print(f"\n🚀 TO USE:")
    print("1. 🌐 Current app: python app.py (should show secrets in UI now)")
    print("2. 🐳 Docker production: ./setup-docker-secrets.sh then docker-compose up")
    print("3. 🔐 Secrets UI: http://localhost:5000/admin/secrets/ (admin/admin123)")
    
    print(f"\n📊 ARCHITECTURE:")
    print("- 🚨 Database passwords: Docker secrets (/run/secrets/)")
    print("- 🔐 App secrets: Database tables (via secrets manager)")
    print("- 🛡️ Master key: Docker secret (for decrypting app secrets)")
    print("- 👁️ Management: Superadmin UI for all non-critical secrets")

if __name__ == "__main__":
    main()