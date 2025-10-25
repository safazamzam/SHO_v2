#!/usr/bin/env python3
"""
Comprehensive Secrets and Configuration Analysis
This script scans the entire application to identify all secrets, credentials, 
and configuration values that should be managed through the secrets management system.
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app import app
from models.models import db
from models.secrets_manager import HybridSecretsManager

def analyze_application_secrets():
    """Analyze all secrets and configurations in the application"""
    
    # Initialize Flask app context
    with app.app_context():
        print("🔍 COMPREHENSIVE SECRETS & CONFIGURATION ANALYSIS")
        print("=" * 60)
        
        # Get master key
        master_key = os.environ.get('SECRETS_MASTER_KEY')
        if not master_key:
            print("❌ SECRETS_MASTER_KEY not found in environment")
            return
        
        # Initialize secrets manager
        try:
            secrets_manager = HybridSecretsManager(db.session, master_key)
            print(f"✅ Secrets manager initialized with key: {master_key[:10]}...")
        except Exception as e:
            print(f"❌ Failed to initialize secrets manager: {e}")
            return
        
        print("\n1. CURRENT SECRETS IN DATABASE:")
        print("-" * 40)
        try:
            current_secrets = secrets_manager.list_secrets()
            if current_secrets:
                for secret in current_secrets:
                    print(f"   🔐 {secret.key} ({secret.category})")
                    print(f"      └─ Updated: {secret.updated_at}")
            else:
                print("   📭 No secrets found in database")
        except Exception as e:
            print(f"   ❌ Error listing secrets: {e}")
        
        print("\n2. CONFIGURATION VALUES FROM CONFIG.PY:")
        print("-" * 40)
        
        # Email/SMTP Configuration
        print("   📧 EMAIL/SMTP CONFIGURATION:")
        smtp_configs = {
            'SMTP_SERVER': app.config.get('MAIL_SERVER'),
            'SMTP_PORT': app.config.get('MAIL_PORT'),
            'SMTP_USERNAME': app.config.get('MAIL_USERNAME'),
            'SMTP_PASSWORD': app.config.get('MAIL_PASSWORD'),
            'TEAM_EMAIL': app.config.get('MAIL_DEFAULT_SENDER'),
        }
        
        for key, value in smtp_configs.items():
            status = "🔒 SET" if value else "❌ NOT SET"
            if key == 'SMTP_PASSWORD' and value == 'uovrivxvitovrjcu':
                status = "🚨 EXPOSED DEFAULT!"
            print(f"      {key}: {status}")
        
        # ServiceNow Configuration
        print("\n   🔧 SERVICENOW CONFIGURATION:")
        servicenow_configs = {
            'SERVICENOW_INSTANCE': app.config.get('SERVICENOW_INSTANCE'),
            'SERVICENOW_USERNAME': app.config.get('SERVICENOW_USERNAME'),
            'SERVICENOW_PASSWORD': app.config.get('SERVICENOW_PASSWORD'),
            'SERVICENOW_API_VERSION': app.config.get('SERVICENOW_API_VERSION'),
            'SERVICENOW_TIMEOUT': app.config.get('SERVICENOW_TIMEOUT'),
            'SERVICENOW_ENABLED': app.config.get('SERVICENOW_ENABLED'),
            'SERVICENOW_ASSIGNMENT_GROUPS': app.config.get('SERVICENOW_ASSIGNMENT_GROUPS'),
        }
        
        for key, value in servicenow_configs.items():
            status = "🔒 SET" if value else "❌ NOT SET"
            print(f"      {key}: {status}")
        
        # SSO/OAuth Configuration
        print("\n   🔐 SSO/OAUTH CONFIGURATION:")
        sso_configs = {
            'SSO_ENCRYPTION_KEY': app.config.get('SSO_ENCRYPTION_KEY'),
            'GOOGLE_OAUTH_CLIENT_ID': app.config.get('GOOGLE_OAUTH_CLIENT_ID'),
            'GOOGLE_OAUTH_CLIENT_SECRET': app.config.get('GOOGLE_OAUTH_CLIENT_SECRET'),
        }
        
        for key, value in sso_configs.items():
            status = "🔒 SET" if value else "❌ NOT SET"
            print(f"      {key}: {status}")
        
        # Database Configuration
        print("\n   🗄️ DATABASE CONFIGURATION:")
        db_configs = {
            'DATABASE_URL': app.config.get('DATABASE_URL'),
            'SECRET_KEY': app.config.get('SECRET_KEY'),
        }
        
        for key, value in db_configs.items():
            status = "🔒 SET" if value else "❌ NOT SET"
            if key == 'DATABASE_URL' and value and 'sqlite' in value.lower():
                status += " (SQLite - DEV ONLY)"
            print(f"      {key}: {status}")
        
        print("\n3. ENVIRONMENT VARIABLES ANALYSIS:")
        print("-" * 40)
        
        # Check for environment variables that should be secrets
        env_secrets = [
            'SECRETS_MASTER_KEY',
            'SMTP_SERVER', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD',
            'SERVICENOW_INSTANCE', 'SERVICENOW_USERNAME', 'SERVICENOW_PASSWORD',
            'GOOGLE_OAUTH_CLIENT_ID', 'GOOGLE_OAUTH_CLIENT_SECRET',
            'SSO_ENCRYPTION_KEY', 'DATABASE_URL', 'SECRET_KEY'
        ]
        
        for env_var in env_secrets:
            value = os.environ.get(env_var)
            if value:
                print(f"   ✅ {env_var}: SET (length: {len(value)})")
            else:
                print(f"   ❌ {env_var}: NOT SET")
        
        print("\n4. RECOMMENDED SECRETS MIGRATION:")
        print("-" * 40)
        
        # Secrets that should be moved to the database
        recommended_migrations = {
            'EXTERNAL_APIS': [
                'SERVICENOW_INSTANCE',
                'SERVICENOW_USERNAME', 
                'SERVICENOW_PASSWORD',
                'GOOGLE_OAUTH_CLIENT_ID',
                'GOOGLE_OAUTH_CLIENT_SECRET'
            ],
            'APPLICATION_CONFIG': [
                'SMTP_SERVER',
                'SMTP_PORT',
                'SMTP_USERNAME', 
                'SMTP_PASSWORD',
                'TEAM_EMAIL'
            ],
            'FEATURE_CONTROLS': [
                'SERVICENOW_API_VERSION',
                'SERVICENOW_TIMEOUT',
                'SERVICENOW_ENABLED',
                'SERVICENOW_ASSIGNMENT_GROUPS'
            ],
            'CRITICAL_SECRETS': [
                'SECRETS_MASTER_KEY',
                'SECRET_KEY',
                'SSO_ENCRYPTION_KEY',
                'DATABASE_URL'
            ]
        }
        
        total_recommended = 0
        
        for category, secrets_list in recommended_migrations.items():
            print(f"\n   📂 {category}:")
            for secret in secrets_list:
                env_value = os.environ.get(secret)
                config_value = app.config.get(secret) if hasattr(app.config, 'get') else None
                
                if env_value or config_value:
                    print(f"      ✅ {secret} - READY TO MIGRATE")
                    total_recommended += 1
                else:
                    print(f"      ⚠️ {secret} - NOT SET")
        
        print(f"\n5. SUMMARY:")
        print("-" * 40)
        current_count = len(current_secrets) if current_secrets else 0
        print(f"   📊 Current secrets in database: {current_count}")
        print(f"   📊 Recommended for migration: {total_recommended}")
        print(f"   📊 Total secrets to manage: {total_recommended}")
        
        print(f"\n6. SECURITY ASSESSMENT:")
        print("-" * 40)
        
        # Security issues
        issues = []
        warnings = []
        
        # Check for exposed default password
        if app.config.get('MAIL_PASSWORD') == 'uovrivxvitovrjcu':
            issues.append("🚨 CRITICAL: Default Gmail password exposed!")
        
        # Check for SQLite in production
        db_url = app.config.get('DATABASE_URL', '')
        if 'sqlite' in db_url.lower():
            warnings.append("⚠️ Using SQLite (not recommended for production)")
        
        # Check for missing critical secrets
        critical_missing = []
        for secret in ['SECRET_KEY', 'SSO_ENCRYPTION_KEY']:
            if not app.config.get(secret):
                critical_missing.append(secret)
        
        if critical_missing:
            issues.append(f"❌ Missing critical secrets: {', '.join(critical_missing)}")
        
        # Print issues
        if issues:
            print("   🚨 SECURITY ISSUES:")
            for issue in issues:
                print(f"      {issue}")
        
        if warnings:
            print("   ⚠️ WARNINGS:")
            for warning in warnings:
                print(f"      {warning}")
        
        if not issues and not warnings:
            print("   ✅ No major security issues detected")
        
        print(f"\n7. NEXT STEPS:")
        print("-" * 40)
        print("   1. 🔐 Migrate secrets from environment to encrypted database")
        print("   2. 🚨 Change exposed Gmail password immediately")
        print("   3. 🔒 Set strong SECRET_KEY for production")
        print("   4. 🗄️ Configure production database (PostgreSQL)")
        print("   5. 🔑 Rotate all secrets before production deployment")
        
        return {
            'current_secrets': current_count,
            'recommended_migrations': total_recommended,
            'security_issues': len(issues),
            'warnings': len(warnings)
        }

if __name__ == "__main__":
    # Set the master key if not already set
    if not os.environ.get('SECRETS_MASTER_KEY'):
        os.environ['SECRETS_MASTER_KEY'] = 'Ll8LcS_EcS8zn1XfecvQVjAcT1Hf_O74uLmfYnXHr3k='
    
    try:
        results = analyze_application_secrets()
        print(f"\n✅ Analysis completed successfully!")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()