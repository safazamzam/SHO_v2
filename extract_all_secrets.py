#!/usr/bin/env python3
"""
Database secrets extractor for the Shift Handover Application
This script will extract all secrets from the database with their actual values
"""

import os
import sys
sys.path.append('.')

from app import app, db
from models.secrets_manager import HybridSecretsManager  
from models.smtp_config import SMTPConfig
from sqlalchemy import text

def get_all_database_secrets():
    """Extract all secrets from the database"""
    with app.app_context():
        print("=" * 80)
        print("DATABASE SECRETS EXTRACTION")
        print("=" * 80)
        
        # 1. SMTP Configuration Secrets
        print("\n1. SMTP CONFIGURATION SECRETS")
        print("-" * 50)
        
        try:
            smtp_configs = SMTPConfig.query.all()
            for config in smtp_configs:
                value = config.config_value
                if config.encrypted:
                    try:
                        # Try to decrypt if possible
                        from cryptography.fernet import Fernet
                        import base64
                        
                        # Get the master key from environment
                        master_key = os.environ.get('SECRETS_MASTER_KEY')
                        if master_key:
                            fernet = Fernet(master_key.encode())
                            # Decrypt if it's encrypted
                            if value and value != '***ENCRYPTED***':
                                try:
                                    decoded_value = base64.b64decode(value.encode())
                                    decrypted_value = fernet.decrypt(decoded_value).decode()
                                    value = decrypted_value
                                except:
                                    value = "[ENCRYPTED - Cannot decrypt]"
                            else:
                                value = "[ENCRYPTED - No value]"
                        else:
                            value = "[ENCRYPTED - No master key]"
                    except Exception as e:
                        value = f"[ENCRYPTION ERROR: {e}]"
                
                status = "🔒 [ENCRYPTED]" if config.encrypted else "🔓 [PLAIN]"
                print(f"   🔑 {config.config_key}: {value} {status}")
        except Exception as e:
            print(f"❌ Error accessing SMTP configs: {e}")
        
        # 2. Application Secrets (HybridSecretsManager)
        print("\n\n2. APPLICATION SECRETS (HybridSecretsManager)")
        print("-" * 50)
        
        try:
            # Initialize the secrets manager with db session
            secrets_manager = HybridSecretsManager(db.session)
            secrets_list = secrets_manager.list_secrets()
            
            for secret in secrets_list:
                key_name = secret.get('key_name', 'Unknown')
                value = secret.get('value', '[NO VALUE]')
                encrypted = secret.get('encrypted', False)
                description = secret.get('description', '')
                category = secret.get('category', 'General')
                
                status = "🔒 [ENCRYPTED]" if encrypted else "🔓 [PLAIN]"
                print(f"   🔑 {key_name}: {value} {status}")
                if description:
                    print(f"      📝 {description}")
                print(f"      📂 Category: {category}")
                print()
                
        except Exception as e:
            print(f"❌ Error accessing HybridSecretsManager: {e}")
        
        # 3. Direct Database Query for any other secrets
        print("\n\n3. DIRECT DATABASE QUERY - ALL SECRET TABLES")
        print("-" * 50)
        
        try:
            # Check for any tables that might contain secrets
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = [row[0] for row in result.fetchall()]
            
            print("📊 Database Tables Found:")
            for table in tables:
                print(f"   📁 {table}")
            
            # Check specific tables for secrets
            secret_tables = ['secrets', 'application_secrets', 'smtp_config', 'sso_config']
            
            for table in secret_tables:
                if table in tables:
                    print(f"\n🔍 Examining table: {table}")
                    try:
                        result = db.session.execute(text(f"SELECT * FROM {table}"))
                        rows = result.fetchall()
                        columns = result.keys()
                        
                        for row in rows:
                            row_dict = dict(zip(columns, row))
                            print(f"   📄 Record: {row_dict}")
                    except Exception as e:
                        print(f"   ❌ Error querying {table}: {e}")
        except Exception as e:
            print(f"❌ Error in direct database query: {e}")

def get_environment_secrets():
    """Get all environment variables that contain secrets"""
    print("\n\n4. ENVIRONMENT VARIABLES (COMPLETE LIST)")
    print("-" * 50)
    
    # All environment variables that might contain secrets
    secret_env_vars = [
        'SECRET_KEY', 'FLASK_SECRET_KEY', 'SECRETS_MASTER_KEY',
        'DATABASE_URL', 'DATABASE_PASSWORD', 'DB_PASSWORD',
        'SMTP_PASSWORD', 'EMAIL_PASSWORD', 'GMAIL_PASSWORD',
        'SERVICENOW_PASSWORD', 'SNOW_PASSWORD', 'SERVICENOW_INSTANCE', 'SERVICENOW_USERNAME',
        'API_KEY', 'ACCESS_TOKEN', 'AUTH_TOKEN',
        'MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_SERVER',
        'SSO_ENCRYPTION_KEY', 'GOOGLE_OAUTH_CLIENT_ID', 'GOOGLE_OAUTH_CLIENT_SECRET'
    ]
    
    found_vars = []
    for var_name in secret_env_vars:
        value = os.environ.get(var_name)
        if value:
            found_vars.append((var_name, value))
            print(f"🌍 {var_name}: {value}")
    
    # Also check for any other environment variables that might contain secrets
    print(f"\n📊 Total secret environment variables found: {len(found_vars)}")
    
    return found_vars

def check_hardcoded_secrets():
    """Check for specific hardcoded secrets in key files"""
    print("\n\n5. CRITICAL HARDCODED SECRETS IN KEY FILES")
    print("-" * 50)
    
    # Check specific critical files
    critical_files = ['app.py', 'config.py', '.env']
    
    for filename in critical_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                print(f"\n📁 {filename}:")
                
                # Look for specific patterns
                if 'supersecretkey' in content:
                    print("   ⚠️ FOUND: Default Flask secret key 'supersecretkey'")
                if 'admin123' in content:
                    print("   ⚠️ FOUND: Default password 'admin123'")
                if 'uovrivxvitovrjcu' in content:
                    print("   ⚠️ FOUND: Gmail app password 'uovrivxvitovrjcu'")
                if 'dev284357.service-now.com' in content:
                    print("   ⚠️ FOUND: ServiceNow instance URL")
                if 'f*X=u2QeWeP2' in content:
                    print("   ⚠️ FOUND: ServiceNow password")
                    
            except Exception as e:
                print(f"   ❌ Error reading {filename}: {e}")

def main():
    """Main function"""
    print("COMPREHENSIVE SECRETS EXTRACTION")
    print("Extracting all secrets with their actual values...")
    print()
    
    get_all_database_secrets()
    env_secrets = get_environment_secrets()
    check_hardcoded_secrets()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✅ All secrets extracted and displayed above")
    print("⚠️  Please secure any exposed credentials immediately")
    print("🔒 Consider moving all secrets to the centralized management system")
    print("=" * 80)

if __name__ == "__main__":
    main()