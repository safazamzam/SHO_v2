#!/usr/bin/env python3
"""
Database Secrets Initialization Script
This script populates the database with initial configuration from your backup .env file
"""

import os
import sys
from flask import Flask
from config import Config
from models.models import db

def create_app():
    """Create Flask app for database operations"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def populate_initial_secrets(secrets_manager):
    """Populate database with initial secrets from your backup configuration"""
    
    # Import SecretCategory here to avoid circular imports
    from models.secrets_manager import SecretCategory
    
    # SMTP Configuration
    smtp_secrets = [
        ('smtp_server', 'smtp.gmail.com', SecretCategory.EXTERNAL, 'SMTP server hostname'),
        ('smtp_port', '587', SecretCategory.EXTERNAL, 'SMTP server port'),
        ('smtp_username', 'mdsajid020@gmail.com', SecretCategory.EXTERNAL, 'SMTP username/email'),
        ('smtp_password', 'uovrivxvitovrjcu', SecretCategory.EXTERNAL, 'SMTP password/app password'),
        ('smtp_from', 'mdsajid020@gmail.com', SecretCategory.EXTERNAL, 'Default FROM email address'),
    ]
    
    # ServiceNow Configuration
    servicenow_secrets = [
        ('servicenow_instance', 'https://dev284357.service-now.com', SecretCategory.EXTERNAL, 'ServiceNow instance URL'),
        ('servicenow_username', 'admin', SecretCategory.EXTERNAL, 'ServiceNow username'),
        ('servicenow_password', 'f*X=u2QeWeP2', SecretCategory.EXTERNAL, 'ServiceNow password'),
        ('servicenow_timeout', '30', SecretCategory.EXTERNAL, 'ServiceNow API timeout (seconds)'),
        ('servicenow_assignment_groups', 'Supply Chain - L2', SecretCategory.EXTERNAL, 'ServiceNow assignment groups to monitor'),
        ('servicenow_enabled', 'true', SecretCategory.EXTERNAL, 'Enable ServiceNow integration'),
    ]
    
    # Application Configuration
    app_secrets = [
        ('session_timeout', '3600', SecretCategory.APPLICATION, 'User session timeout (seconds)'),
        ('max_workers', '4', SecretCategory.APPLICATION, 'Maximum worker processes'),
        ('log_level', 'INFO', SecretCategory.APPLICATION, 'Application log level'),
    ]
    
    all_secrets = smtp_secrets + servicenow_secrets + app_secrets
    
    created_count = 0
    updated_count = 0
    
    for key, value, category, description in all_secrets:
        try:
            existing = secrets_manager.get_secret(key)
            if existing is None:
                secrets_manager.set_secret(key, value, category, description)
                print(f"✅ Created secret: {key}")
                created_count += 1
            else:
                print(f"ℹ️ Secret already exists: {key}")
        except Exception as e:
            print(f"❌ Error creating secret {key}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Created: {created_count} secrets")
    print(f"   Existing: {len(all_secrets) - created_count} secrets")
    print(f"   Total: {len(all_secrets)} secrets")

def main():
    """Main initialization function"""
    print("🔐 Initializing Database Secrets Management")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Import secrets manager functions
            from models.secrets_manager import init_secrets_manager, secrets_manager
            
            # Initialize secrets manager
            master_key = app.config.get('SECRETS_MASTER_KEY')
            if not master_key:
                print("❌ SECRETS_MASTER_KEY not found in configuration")
                print("💡 This is normal for development - using generated key")
                return False
            
            # Create database tables if they don't exist
            db.create_all()
            print("✅ Database tables created/verified")
            
            # Initialize secrets manager with db session and master key
            initialized_manager = init_secrets_manager(db.session, master_key)
            print(f"✅ Secrets manager initialized: {initialized_manager is not None}")
            
            # Populate initial secrets
            populate_initial_secrets(initialized_manager)
            
            print("\n🎉 Database secrets initialization completed successfully!")
            print("\n📋 Next steps:")
            print("1. Start your application with: docker-compose -f docker-compose.secure.yml up")
            print("2. Access the Secrets Management Dashboard to verify configuration")
            print("3. Test SMTP and ServiceNow connections")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during initialization: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)