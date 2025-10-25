#!/usr/bin/env python3
"""
🔧 SECRETS RECOVERY AND RE-ENCRYPTION
Fix the master key issue and recover the secrets
"""

from app import app, db
from sqlalchemy import text
from cryptography.fernet import Fernet
import os

def check_master_key_issue():
    """Check if the master key issue is causing problems"""
    with app.app_context():
        print("🔍 DIAGNOSING MASTER KEY ISSUE:")
        print("=" * 50)
        
        # Check current environment key
        current_key = os.environ.get('SECRETS_MASTER_KEY')
        print(f"Current SECRETS_MASTER_KEY: {current_key[:20]}..." if current_key else "Not set")
        
        # Try to decrypt with current key
        try:
            from models.secrets_manager import HybridSecretsManager
            secrets_manager = HybridSecretsManager(db.session)
            
            # Try to list secrets
            secrets = secrets_manager.list_secrets()
            print(f"✅ Successfully accessed {len(secrets)} secrets")
            return True
            
        except Exception as e:
            print(f"❌ Cannot access secrets with current key: {e}")
            return False

def re_encrypt_with_known_values():
    """Re-encrypt secrets with known values and new master key"""
    with app.app_context():
        print("\n🔧 RE-ENCRYPTING SECRETS WITH KNOWN VALUES:")
        print("=" * 50)
        
        try:
            # Clear all existing secrets first
            with db.engine.connect() as connection:
                connection.execute(text("DELETE FROM secret_store;"))
                connection.commit()
                print("🗑️ Cleared existing encrypted secrets")
            
            # Initialize with new master key
            new_master_key = "tSo-GG44Oa9MGWQmXv470mdCPxMRwhuejU87skv22ZQ="
            os.environ['SECRETS_MASTER_KEY'] = new_master_key
            
            from models.secrets_manager import HybridSecretsManager
            secrets_manager = HybridSecretsManager(db.session, new_master_key)
            
            # Re-create secrets with known values
            secrets_to_create = [
                ('SMTP_USERNAME', 'mdsajid020@gmail.com', 'External APIs', 'SMTP email username'),
                ('SMTP_PASSWORD', 'uovrivxvitovrjcu', 'External APIs', 'SMTP email password - NEEDS ROTATION'),
                ('TEAM_EMAIL', 'mdsajid020@gmail.com', 'Application Configuration', 'Team email address'),
                ('SERVICENOW_INSTANCE', 'dev284357.service-now.com', 'External APIs', 'ServiceNow instance URL'),
                ('SERVICENOW_USERNAME', 'admin', 'External APIs', 'ServiceNow username'),
                ('SERVICENOW_PASSWORD', 'f*X=u2QeWeP2', 'External APIs', 'ServiceNow password - NEEDS ROTATION'),
                ('SERVICENOW_TIMEOUT', '30', 'Application Configuration', 'ServiceNow API timeout'),
                ('SERVICENOW_ENABLED', 'true', 'Feature Controls', 'Enable ServiceNow integration'),
            ]
            
            success_count = 0
            for key, value, category, description in secrets_to_create:
                try:
                    result = secrets_manager.set_secret(key, value, category, description)
                    if result:
                        print(f"✅ Re-encrypted: {key}")
                        success_count += 1
                    else:
                        print(f"❌ Failed to encrypt: {key}")
                except Exception as e:
                    print(f"❌ Error encrypting {key}: {e}")
            
            print(f"\n🎉 Successfully re-encrypted {success_count}/{len(secrets_to_create)} secrets")
            return success_count == len(secrets_to_create)
            
        except Exception as e:
            print(f"❌ Re-encryption failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_secrets_access():
    """Test that secrets can now be accessed"""
    with app.app_context():
        print("\n🧪 TESTING SECRETS ACCESS:")
        print("=" * 50)
        
        try:
            from models.secrets_manager import HybridSecretsManager
            secrets_manager = HybridSecretsManager(db.session)
            
            # Test reading each secret
            test_keys = ['SMTP_USERNAME', 'SMTP_PASSWORD', 'SERVICENOW_INSTANCE', 'SERVICENOW_USERNAME']
            
            for key in test_keys:
                try:
                    value = secrets_manager.get_secret(key)
                    if value:
                        print(f"✅ {key}: {value[:10]}..." if len(value) > 10 else f"✅ {key}: {value}")
                    else:
                        print(f"❌ {key}: Not found")
                except Exception as e:
                    print(f"❌ {key}: Error - {e}")
            
            # Test listing all secrets
            secrets = secrets_manager.list_secrets(include_values=False)
            print(f"\n📊 Total secrets accessible: {len(secrets)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Testing failed: {e}")
            return False

def main():
    print("🔧 SECRETS RECOVERY AND RE-ENCRYPTION")
    print("=" * 60)
    
    # Check if current key works
    if not check_master_key_issue():
        print("\n🔧 Master key issue detected. Re-encrypting secrets...")
        
        if re_encrypt_with_known_values():
            print("\n✅ Re-encryption successful!")
            test_secrets_access()
        else:
            print("\n❌ Re-encryption failed!")
    else:
        print("\n✅ Secrets are accessible with current key")
        test_secrets_access()
    
    print(f"\n📋 NEXT STEPS:")
    print("=" * 50)
    print("1. 🔑 Set master key: $env:SECRETS_MASTER_KEY = \"tSo-GG44Oa9MGWQmXv470mdCPxMRwhuejU87skv22ZQ=\"")
    print("2. 🚀 Start app: python app.py")
    print("3. 🌐 Access UI: http://127.0.0.1:5000/admin/secrets/")
    print("4. 🔄 Rotate exposed passwords immediately!")

if __name__ == "__main__":
    main()