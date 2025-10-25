#!/usr/bin/env python3
"""
Verify Database Secrets Configuration
This script checks that all secrets are properly stored and accessible
"""

import os
from flask import Flask
from config import Config
from models.models import db
from models.secrets_manager import init_secrets_manager, secrets_manager

def create_app():
    """Create Flask app for database operations"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def verify_secrets(secrets_mgr):
    """Verify all secrets are properly stored and accessible"""
    
    required_secrets = [
        # SMTP Configuration
        'smtp_server',
        'smtp_port', 
        'smtp_username',
        'smtp_password',
        'smtp_from',
        
        # ServiceNow Configuration
        'servicenow_instance',
        'servicenow_username',
        'servicenow_password',
        'servicenow_timeout',
        'servicenow_assignment_groups',
        'servicenow_enabled',
        
        # Application Configuration
        'session_timeout',
        'max_workers',
        'log_level',
    ]
    
    print("🔍 Verifying Database Secrets")
    print("=" * 40)
    
    missing_secrets = []
    accessible_secrets = []
    
    for secret_name in required_secrets:
        try:
            value = secrets_mgr.get_secret(secret_name)
            if value is not None:
                # Mask sensitive values for display
                if 'password' in secret_name.lower() or 'key' in secret_name.lower():
                    display_value = '••••••••' if len(value) > 4 else '••••'
                else:
                    display_value = value[:50] + '...' if len(value) > 50 else value
                
                print(f"✅ {secret_name}: {display_value}")
                accessible_secrets.append(secret_name)
            else:
                print(f"❌ {secret_name}: NOT FOUND")
                missing_secrets.append(secret_name)
        except Exception as e:
            print(f"❌ {secret_name}: ERROR - {e}")
            missing_secrets.append(secret_name)
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Accessible: {len(accessible_secrets)}")
    print(f"   ❌ Missing: {len(missing_secrets)}")
    print(f"   📋 Total: {len(required_secrets)}")
    
    if missing_secrets:
        print(f"\n⚠️ Missing secrets:")
        for secret in missing_secrets:
            print(f"   - {secret}")
        print(f"\n💡 Run 'python init_database_secrets.py' to populate missing secrets")
        return False
    else:
        print(f"\n🎉 All secrets are properly configured!")
        return True

def verify_docker_secrets():
    """Verify critical Docker secrets are accessible"""
    print("\n🐳 Verifying Docker Secrets")
    print("=" * 30)
    
    critical_secrets = ['secret_key', 'mysql_user_password', 'secrets_master_key']
    
    for secret_name in critical_secrets:
        secret_file = f"/run/secrets/{secret_name}"
        if os.path.exists(secret_file):
            try:
                with open(secret_file, 'r') as f:
                    value = f.read().strip()
                    if value:
                        print(f"✅ {secret_name}: Available")
                    else:
                        print(f"❌ {secret_name}: Empty file")
            except Exception as e:
                print(f"❌ {secret_name}: Read error - {e}")
        else:
            # Check environment variables as fallback
            env_value = os.environ.get(secret_name.upper())
            if env_value:
                print(f"⚠️ {secret_name}: Available from environment (not Docker secret)")
            else:
                print(f"❌ {secret_name}: Not found")

def main():
    """Main verification function"""
    print("Database Secrets Configuration Verification")
    print("=" * 55)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Verify Docker secrets first
            verify_docker_secrets()
            
            # Initialize secrets manager
            master_key = app.config.get('SECRETS_MASTER_KEY')
            if not master_key:
                print("\n❌ SECRETS_MASTER_KEY not available")
                print("💡 Make sure Docker secrets are properly configured")
                return False
            
            # Import and initialize secrets manager
            from models.secrets_manager import init_secrets_manager
            secrets_mgr = init_secrets_manager(db.session, master_key)
            
            # Verify database secrets
            success = verify_secrets(secrets_mgr)
            
            if success:
                print(f"\n✅ Configuration verification completed successfully!")
                print(f"\n📋 Your application is ready to use:")
                print(f"   - SMTP email functionality")
                print(f"   - ServiceNow integration") 
                print(f"   - Secure secrets management")
            
            return success
            
        except Exception as e:
            print(f"❌ Error during verification: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    main()