#!/usr/bin/env python3
"""
Comprehensive secrets and configuration scanner for the Shift Handover Application
This script will identify all secrets, configurations, credentials, and sensitive data
"""

import os
import re
import json
from pathlib import Path

def scan_file_for_secrets(file_path):
    """Scan a file for potential secrets and configurations"""
    secrets_found = []
    
    # Common secret patterns
    secret_patterns = [
        # API Keys and tokens
        (r'["\']?(?:api[_-]?key|apikey)["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'API Key'),
        (r'["\']?(?:secret[_-]?key|secretkey)["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'Secret Key'),
        (r'["\']?(?:access[_-]?token|accesstoken)["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'Access Token'),
        (r'["\']?(?:auth[_-]?token|authtoken)["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'Auth Token'),
        
        # Database credentials
        (r'["\']?(?:db[_-]?password|database[_-]?password)["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'Database Password'),
        (r'["\']?(?:db[_-]?user|database[_-]?user)["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'Database User'),
        (r'["\']?(?:db[_-]?host|database[_-]?host)["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'Database Host'),
        (r'["\']?(?:connection[_-]?string|connectionstring)["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'Connection String'),
        
        # Email/SMTP credentials
        (r'["\']?(?:smtp[_-]?password|mail[_-]?password)["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'SMTP Password'),
        (r'["\']?(?:smtp[_-]?user|mail[_-]?user)["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'SMTP User'),
        (r'["\']?(?:email[_-]?password|gmail[_-]?password)["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'Email Password'),
        
        # ServiceNow credentials
        (r'["\']?(?:servicenow[_-]?password|snow[_-]?password)["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'ServiceNow Password'),
        (r'["\']?(?:servicenow[_-]?user|snow[_-]?user)["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'ServiceNow User'),
        (r'["\']?(?:servicenow[_-]?instance|snow[_-]?instance)["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'ServiceNow Instance'),
        
        # General passwords and secrets
        (r'["\']?password["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'Password'),
        (r'["\']?secret["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'Secret'),
        (r'["\']?key["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'Key'),
        
        # URLs and endpoints
        (r'["\']?(?:url|endpoint)["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'URL/Endpoint'),
        
        # Configuration values
        (r'["\']?(?:host|hostname)["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'Host'),
        (r'["\']?(?:port)["\']?\s*[:=]\s*["\']?(\d+)["\']?', 'Port'),
        (r'["\']?(?:timeout)["\']?\s*[:=]\s*["\']?(\d+)["\']?', 'Timeout'),
        
        # Flask/App specific
        (r'SECRET_KEY\s*=\s*["\']([^"\']+)["\']', 'Flask Secret Key'),
        (r'DEBUG\s*=\s*([TrueFalse]+)', 'Debug Mode'),
        (r'SQLALCHEMY_DATABASE_URI\s*=\s*["\']([^"\']+)["\']', 'Database URI'),
    ]
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        for pattern, secret_type in secret_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if match and len(match.strip()) > 0 and match.strip() not in ['', 'None', 'null', 'undefined']:
                    secrets_found.append({
                        'file': str(file_path),
                        'type': secret_type,
                        'value': match.strip(),
                        'pattern': pattern
                    })
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return secrets_found

def scan_directory(directory):
    """Scan directory for secrets"""
    all_secrets = []
    
    # File extensions to scan
    extensions = ['.py', '.js', '.html', '.json', '.yaml', '.yml', '.txt', '.cfg', '.ini', '.conf', '.env']
    
    # Files to specifically check
    important_files = [
        'config.py', 'app.py', 'settings.py', '.env', '.env.local', 
        'requirements.txt', 'package.json', 'docker-compose.yml'
    ]
    
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            file_path = Path(root) / file
            
            # Check important files or files with relevant extensions
            if file in important_files or any(file.endswith(ext) for ext in extensions):
                secrets = scan_file_for_secrets(file_path)
                all_secrets.extend(secrets)
    
    return all_secrets

def check_database_secrets():
    """Check for secrets in the database"""
    try:
        # Import Flask app and database
        import sys
        sys.path.append('.')
        
        from app import app, db
        from models.secrets_manager import HybridSecretsManager
        from models.smtp_config import SMTPConfig
        
        with app.app_context():
            db_secrets = []
            
            # Check HybridSecretsManager secrets
            try:
                secrets_manager = HybridSecretsManager()
                secrets_list = secrets_manager.list_secrets()
                
                for secret in secrets_list:
                    db_secrets.append({
                        'source': 'Database (HybridSecretsManager)',
                        'key': secret.get('key_name', 'Unknown'),
                        'value': secret.get('value', '[ENCRYPTED]'),
                        'encrypted': secret.get('encrypted', False),
                        'description': secret.get('description', ''),
                        'category': secret.get('category', 'General')
                    })
            except Exception as e:
                print(f"Error accessing HybridSecretsManager: {e}")
            
            # Check SMTP configurations
            try:
                smtp_configs = SMTPConfig.query.all()
                for config in smtp_configs:
                    value = config.get_decrypted_value() if config.encrypted else config.config_value
                    db_secrets.append({
                        'source': 'Database (SMTP Config)',
                        'key': config.config_key,
                        'value': value if not config.encrypted else '[ENCRYPTED]',
                        'encrypted': config.encrypted,
                        'description': f'SMTP configuration for {config.config_key}',
                        'category': 'SMTP'
                    })
            except Exception as e:
                print(f"Error accessing SMTP configs: {e}")
                
            return db_secrets
            
    except Exception as e:
        print(f"Error checking database secrets: {e}")
        return []

def check_environment_variables():
    """Check environment variables for secrets"""
    env_secrets = []
    
    # Common secret environment variable names
    secret_env_vars = [
        'SECRET_KEY', 'FLASK_SECRET_KEY', 'SECRETS_MASTER_KEY',
        'DATABASE_URL', 'DATABASE_PASSWORD', 'DB_PASSWORD',
        'SMTP_PASSWORD', 'EMAIL_PASSWORD', 'GMAIL_PASSWORD',
        'SERVICENOW_PASSWORD', 'SNOW_PASSWORD',
        'API_KEY', 'ACCESS_TOKEN', 'AUTH_TOKEN',
        'MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_SERVER',
        'SERVICENOW_INSTANCE', 'SERVICENOW_USERNAME'
    ]
    
    for var_name in secret_env_vars:
        value = os.environ.get(var_name)
        if value:
            env_secrets.append({
                'source': 'Environment Variable',
                'key': var_name,
                'value': value,
                'type': 'Environment Variable'
            })
    
    return env_secrets

def main():
    """Main function to scan and report all secrets"""
    print("=" * 80)
    print("SHIFT HANDOVER APP - COMPREHENSIVE SECRETS & CONFIGURATION AUDIT")
    print("=" * 80)
    
    workspace_dir = Path(__file__).parent
    
    # 1. Scan files for hardcoded secrets
    print("\n1. SCANNING FILES FOR HARDCODED SECRETS...")
    print("-" * 50)
    
    file_secrets = scan_directory(workspace_dir)
    
    # Group by file
    secrets_by_file = {}
    for secret in file_secrets:
        file_path = secret['file']
        if file_path not in secrets_by_file:
            secrets_by_file[file_path] = []
        secrets_by_file[file_path].append(secret)
    
    total_file_secrets = 0
    for file_path, secrets in secrets_by_file.items():
        rel_path = os.path.relpath(file_path, workspace_dir)
        print(f"\n📁 {rel_path}")
        for secret in secrets:
            print(f"   🔑 {secret['type']}: {secret['value']}")
            total_file_secrets += 1
    
    print(f"\n📊 Total hardcoded secrets found: {total_file_secrets}")
    
    # 2. Check database secrets
    print("\n\n2. CHECKING DATABASE SECRETS...")
    print("-" * 50)
    
    db_secrets = check_database_secrets()
    
    if db_secrets:
        secrets_by_category = {}
        for secret in db_secrets:
            category = secret.get('category', 'General')
            if category not in secrets_by_category:
                secrets_by_category[category] = []
            secrets_by_category[category].append(secret)
        
        for category, secrets in secrets_by_category.items():
            print(f"\n📁 {category} Configuration")
            for secret in secrets:
                status = "🔒 [ENCRYPTED]" if secret.get('encrypted') else "🔓 [PLAIN]"
                print(f"   🔑 {secret['key']}: {secret['value']} {status}")
                if secret.get('description'):
                    print(f"      📝 {secret['description']}")
        
        print(f"\n📊 Total database secrets: {len(db_secrets)}")
    else:
        print("❌ No database secrets found or unable to access database")
    
    # 3. Check environment variables
    print("\n\n3. CHECKING ENVIRONMENT VARIABLES...")
    print("-" * 50)
    
    env_secrets = check_environment_variables()
    
    if env_secrets:
        for secret in env_secrets:
            print(f"🌍 {secret['key']}: {secret['value']}")
        print(f"\n📊 Total environment secrets: {len(env_secrets)}")
    else:
        print("❌ No relevant environment variables found")
    
    # 4. Summary
    print("\n\n4. SUMMARY")
    print("-" * 50)
    
    total_secrets = total_file_secrets + len(db_secrets) + len(env_secrets)
    
    print(f"📊 TOTAL SECRETS AUDIT:")
    print(f"   • Hardcoded in files: {total_file_secrets}")
    print(f"   • Stored in database: {len(db_secrets)}")
    print(f"   • Environment variables: {len(env_secrets)}")
    print(f"   • TOTAL: {total_secrets}")
    
    # 5. Security recommendations
    print("\n\n5. SECURITY RECOMMENDATIONS")
    print("-" * 50)
    
    if total_file_secrets > 0:
        print("⚠️  CRITICAL: Hardcoded secrets found in files!")
        print("   → Move these to the centralized secrets management system")
        print("   → Use environment variables for sensitive configuration")
    
    if len(env_secrets) > 0:
        print("✅ Environment variables are being used")
        print("   → Ensure these are not committed to version control")
    
    if len(db_secrets) > 0:
        print("✅ Database secrets management is active")
        print("   → Ensure master key is properly secured")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()