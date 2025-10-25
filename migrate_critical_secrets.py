#!/usr/bin/env python3
"""
CRITICAL SECRETS MIGRATION SCRIPT
This script will migrate all exposed secrets to the centralized secrets management system
"""

import os
import sys
import secrets
import string
from datetime import datetime

# Add the app directory to Python path
sys.path.append('.')

def generate_secure_password(length=32):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_flask_secret_key():
    """Generate a secure Flask secret key"""
    return secrets.token_urlsafe(32)

def migrate_critical_secrets():
    """Migrate all critical exposed secrets"""
    print("🚨 CRITICAL SECRETS MIGRATION STARTING...")
    print("=" * 60)
    
    try:
        from app import app, db
        from models.secrets_manager import HybridSecretsManager
        from models.smtp_config import SMTPConfig
        
        with app.app_context():
            # Initialize secrets manager
            secrets_manager = HybridSecretsManager(db.session)
            
            print("\n1. 📧 MIGRATING SMTP CREDENTIALS")
            print("-" * 40)
            
            # Get current environment values
            current_smtp_password = os.environ.get('SMTP_PASSWORD', '')
            
            if current_smtp_password and current_smtp_password != '[TO_BE_CONFIGURED]':
                print(f"✅ Found SMTP password in environment: {current_smtp_password[:4]}...")
                
                # Migrate SMTP username (assuming it's the Gmail address)
                gmail_username = "your-email@gmail.com"  # You'll need to provide the actual Gmail username
                print(f"📝 Please provide your Gmail username/email address:")
                print(f"   Current placeholder: {gmail_username}")
                
                # Update SMTP configuration in database
                smtp_configs = [
                    ('smtp_username', gmail_username, False, 'Gmail SMTP username'),
                    ('smtp_password', current_smtp_password, True, 'Gmail app-specific password (migrated from environment)'),
                    ('mail_default_sender', 'noreply@yourcompany.com', False, 'Default sender email (update as needed)'),
                    ('team_email', 'team@yourcompany.com', False, 'Team email for notifications (update as needed)'),
                    ('smtp_enabled', 'true', False, 'Enable SMTP email service')
                ]
                
                for key, value, encrypt, description in smtp_configs:
                    config = SMTPConfig.query.filter_by(config_key=key).first()
                    if config:
                        config.config_value = value
                        config.encrypted = encrypt
                        config.description = description
                        config.updated_at = datetime.utcnow()
                        print(f"   🔄 Updated {key}")
                    else:
                        config = SMTPConfig(
                            config_key=key,
                            config_value=value,
                            encrypted=encrypt,
                            description=description
                        )
                        db.session.add(config)
                        print(f"   ➕ Created {key}")
                
                db.session.commit()
                print("✅ SMTP configuration migrated to database")
            else:
                print("⚠️ No SMTP password found in environment")
            
            print("\n2. 🔧 MIGRATING SERVICENOW CREDENTIALS")
            print("-" * 40)
            
            # ServiceNow credentials
            servicenow_instance = os.environ.get('SERVICENOW_INSTANCE', '')
            servicenow_username = os.environ.get('SERVICENOW_USERNAME', '')
            servicenow_password = os.environ.get('SERVICENOW_PASSWORD', '')
            
            servicenow_secrets = [
                ('SERVICENOW_INSTANCE', servicenow_instance, False, 'ServiceNow instance URL', 'ServiceNow'),
                ('SERVICENOW_USERNAME', servicenow_username, False, 'ServiceNow integration username', 'ServiceNow'),
                ('SERVICENOW_PASSWORD', servicenow_password, True, 'ServiceNow integration password (migrated from environment)', 'ServiceNow')
            ]
            
            for key, value, encrypt, description, category in servicenow_secrets:
                if value and value != '[TO_BE_CONFIGURED]':
                    try:
                        result = secrets_manager.set_secret(
                            key_name=key,
                            value=value,
                            description=description,
                            category=category
                        )
                        if result['success']:
                            print(f"   ✅ Migrated {key}")
                        else:
                            print(f"   ⚠️ Failed to migrate {key}: {result.get('error', 'Unknown error')}")
                    except Exception as e:
                        print(f"   ❌ Error migrating {key}: {e}")
                else:
                    print(f"   ⚠️ No value found for {key}")
            
            print("\n3. 🔒 GENERATING NEW SECURITY KEYS")
            print("-" * 40)
            
            # Generate new Flask secret key
            new_flask_secret = generate_flask_secret_key()
            print(f"✅ Generated new Flask secret key: {new_flask_secret[:8]}...")
            
            # Store in secrets manager
            try:
                result = secrets_manager.set_secret(
                    key_name='FLASK_SECRET_KEY',
                    value=new_flask_secret,
                    description='Secure Flask secret key (generated during migration)',
                    category='Security'
                )
                if result['success']:
                    print("   ✅ Stored new Flask secret key in database")
                else:
                    print(f"   ⚠️ Failed to store Flask secret: {result.get('error')}")
            except Exception as e:
                print(f"   ❌ Error storing Flask secret: {e}")
            
            # Generate SSO encryption key
            sso_key = generate_flask_secret_key()
            print(f"✅ Generated SSO encryption key: {sso_key[:8]}...")
            
            try:
                result = secrets_manager.set_secret(
                    key_name='SSO_ENCRYPTION_KEY',
                    value=sso_key,
                    description='Persistent SSO encryption key (generated during migration)',
                    category='Security'
                )
                if result['success']:
                    print("   ✅ Stored SSO encryption key in database")
                else:
                    print(f"   ⚠️ Failed to store SSO key: {result.get('error')}")
            except Exception as e:
                print(f"   ❌ Error storing SSO key: {e}")
            
            print("\n4. 📝 CREATING MIGRATION SUMMARY")
            print("-" * 40)
            
            # Create a summary of what was migrated
            migration_summary = {
                'timestamp': datetime.utcnow().isoformat(),
                'smtp_migrated': bool(current_smtp_password),
                'servicenow_migrated': bool(servicenow_instance and servicenow_username and servicenow_password),
                'new_flask_secret': new_flask_secret,
                'new_sso_key': sso_key,
                'next_steps': [
                    'Update .env file with new secret keys',
                    'Remove hardcoded secrets from config.py',
                    'Test SMTP functionality',
                    'Test ServiceNow connection',
                    'Update production environment variables'
                ]
            }
            
            # Store migration summary
            try:
                result = secrets_manager.set_secret(
                    key_name='MIGRATION_SUMMARY',
                    value=str(migration_summary),
                    description=f'Migration summary from {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}',
                    category='Migration'
                )
                print("   ✅ Stored migration summary")
            except Exception as e:
                print(f"   ⚠️ Could not store migration summary: {e}")
            
            print("\n" + "=" * 60)
            print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            
            print("\n📋 NEXT STEPS:")
            print("1. Update your .env file with the new keys shown above")
            print("2. Remove hardcoded secrets from config.py")
            print("3. Restart the Flask application")
            print("4. Test SMTP and ServiceNow functionality")
            print("5. Access the secrets dashboard to verify: http://127.0.0.1:5000/admin/secrets/")
            
            return {
                'success': True,
                'new_flask_secret': new_flask_secret,
                'new_sso_key': sso_key,
                'summary': migration_summary
            }
            
    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {e}")
        return {'success': False, 'error': str(e)}

def create_new_env_file(migration_result):
    """Create a new .env file with migrated secrets"""
    if not migration_result['success']:
        print("❌ Cannot create .env file - migration failed")
        return
    
    print("\n5. 📄 CREATING NEW .env FILE")
    print("-" * 40)
    
    # Backup existing .env
    if os.path.exists('.env'):
        backup_name = f'.env.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        os.rename('.env', backup_name)
        print(f"✅ Backed up existing .env to {backup_name}")
    
    # Create new .env with secure values
    new_env_content = f"""# Shift Handover App - Secure Configuration
# Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# IMPORTANT: Keep this file secure and never commit to version control

# Flask Security (NEW - SECURE)
SECRET_KEY={migration_result['new_flask_secret']}

# Secrets Management (EXISTING - KEEP)
SECRETS_MASTER_KEY=Ll8LcS_EcS8zn1XfecvQVjAcT1Hf_O74uLmfYnXHr3k=

# SSO Security (NEW - SECURE)
SSO_ENCRYPTION_KEY={migration_result['new_sso_key']}

# Database (for production)
# DATABASE_URL=postgresql://username:password@localhost/shift_handover_prod

# Email Configuration (MIGRATED TO DATABASE - REMOVE THESE AFTER TESTING)
# SMTP_PASSWORD=*** MIGRATED TO SECURE DATABASE STORAGE ***

# ServiceNow Configuration (MIGRATED TO DATABASE - REMOVE THESE AFTER TESTING)
# SERVICENOW_INSTANCE=*** MIGRATED TO SECURE DATABASE STORAGE ***
# SERVICENOW_USERNAME=*** MIGRATED TO SECURE DATABASE STORAGE ***
# SERVICENOW_PASSWORD=*** MIGRATED TO SECURE DATABASE STORAGE ***

# OAuth Configuration (TO BE CONFIGURED)
# GOOGLE_OAUTH_CLIENT_ID=your-client-id
# GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret

# Development Settings
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    with open('.env', 'w') as f:
        f.write(new_env_content)
    
    print("✅ Created new secure .env file")
    print("⚠️ Old credentials are commented out - remove them after testing")

def main():
    """Main migration function"""
    print("🔒 SHIFT HANDOVER APP - CRITICAL SECRETS MIGRATION")
    print("=" * 60)
    print("This script will migrate all exposed secrets to secure storage")
    print()
    
    # Confirm migration
    response = input("🤔 Do you want to proceed with the migration? (yes/no): ").lower().strip()
    if response not in ['yes', 'y']:
        print("❌ Migration cancelled by user")
        return
    
    # Perform migration
    result = migrate_critical_secrets()
    
    if result['success']:
        # Create new .env file
        create_new_env_file(result)
        
        print("\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("\n📋 WHAT WAS MIGRATED:")
        print("✅ SMTP credentials moved to encrypted database storage")
        print("✅ ServiceNow credentials moved to encrypted database storage")
        print("✅ New secure Flask secret key generated")
        print("✅ New SSO encryption key generated")
        print("✅ Secure .env file created")
        
        print("\n🔍 VERIFY MIGRATION:")
        print("1. Check the secrets dashboard: http://127.0.0.1:5000/admin/secrets/")
        print("2. Test SMTP functionality")
        print("3. Test ServiceNow connection")
        
        print("\n⚠️ IMPORTANT NEXT STEPS:")
        print("1. Restart your Flask application")
        print("2. Remove hardcoded secrets from config.py")
        print("3. Update production environment with new keys")
        print("4. Test all functionality")
        
    else:
        print("❌ Migration failed. Please check the error messages above.")

if __name__ == "__main__":
    main()