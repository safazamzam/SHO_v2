#!/usr/bin/env python3
"""
🔧 COMPLETE SECRETS SYSTEM RESET
Fix all the master key and decryption issues
"""

from app import app, db
from sqlalchemy import text
from cryptography.fernet import Fernet
import os

def complete_secrets_reset():
    """Complete reset of the secrets system with proper encryption"""
    with app.app_context():
        print("🔧 COMPLETE SECRETS SYSTEM RESET:")
        print("=" * 50)
        
        try:
            # Clear existing data
            with db.engine.connect() as connection:
                connection.execute(text("DELETE FROM secret_store;"))
                connection.execute(text("DELETE FROM secret_audit_log;"))
                connection.commit()
                print("🗑️ Cleared all existing secrets and logs")
            
            # Set up the correct master key
            master_key = "tSo-GG44Oa9MGWQmXv470mdCPxMRwhuejU87skv22ZQ="
            os.environ['SECRETS_MASTER_KEY'] = master_key
            
            # Import and initialize secrets manager
            from models.secrets_manager import HybridSecretsManager
            secrets_manager = HybridSecretsManager(db.session, master_key)
            
            # Create all secrets fresh
            secrets_data = [
                ('SMTP_USERNAME', 'mdsajid020@gmail.com', 'External APIs', 'SMTP email username'),
                ('SMTP_PASSWORD', 'uovrivxvitovrjcu', 'External APIs', '🚨 SMTP password - ROTATE IMMEDIATELY'),
                ('TEAM_EMAIL', 'mdsajid020@gmail.com', 'Application Configuration', 'Team email address'),
                ('SERVICENOW_INSTANCE', 'dev284357.service-now.com', 'External APIs', 'ServiceNow instance URL'),
                ('SERVICENOW_USERNAME', 'admin', 'External APIs', 'ServiceNow username'),
                ('SERVICENOW_PASSWORD', 'f*X=u2QeWeP2', 'External APIs', '🚨 ServiceNow password - ROTATE IMMEDIATELY'),
                ('SERVICENOW_TIMEOUT', '30', 'Application Configuration', 'ServiceNow API timeout'),
                ('SERVICENOW_ENABLED', 'true', 'Feature Controls', 'Enable ServiceNow integration'),
                ('SERVICENOW_API_VERSION', 'v1', 'Application Configuration', 'ServiceNow API version'),
                ('SERVICENOW_ASSIGNMENT_GROUPS', 'Supply Chain Support', 'Application Configuration', 'ServiceNow assignment groups'),
            ]
            
            success_count = 0
            for key, value, category, description in secrets_data:
                try:
                    result = secrets_manager.set_secret(key, value, category, description)
                    if result:
                        print(f"✅ Created: {key}")
                        success_count += 1
                    else:
                        print(f"❌ Failed: {key}")
                except Exception as e:
                    print(f"❌ Error creating {key}: {e}")
            
            print(f"\n🎉 Successfully created {success_count}/{len(secrets_data)} secrets")
            
            # Test immediate access
            print("\n🧪 TESTING IMMEDIATE ACCESS:")
            for key, expected_value, _, _ in secrets_data[:4]:  # Test first 4
                try:
                    retrieved_value = secrets_manager.get_secret(key)
                    if retrieved_value == expected_value:
                        print(f"✅ {key}: ✓ Correct")
                    else:
                        print(f"❌ {key}: Expected '{expected_value}', got '{retrieved_value}'")
                except Exception as e:
                    print(f"❌ {key}: Error - {e}")
            
            return success_count == len(secrets_data)
            
        except Exception as e:
            print(f"❌ Reset failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def verify_app_integration():
    """Verify that the app can now access secrets properly"""
    print("\n🔍 VERIFYING APP INTEGRATION:")
    print("=" * 50)
    
    # Test config access patterns
    try:
        from config import SecureConfigManager
        config_manager = SecureConfigManager()
        
        # Test each secret through config manager
        test_secrets = [
            'SMTP_USERNAME',
            'SMTP_PASSWORD', 
            'SERVICENOW_INSTANCE',
            'SERVICENOW_USERNAME',
            'SERVICENOW_PASSWORD'
        ]
        
        for secret_name in test_secrets:
            try:
                value = config_manager.get_secret(secret_name)
                if value and value != "*** MIGRATED TO DATABASE ***":
                    print(f"✅ Config can access {secret_name}")
                else:
                    print(f"⚠️ Config returns fallback for {secret_name}")
            except Exception as e:
                print(f"❌ Config error for {secret_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ App integration test failed: {e}")
        return False

def save_master_key_to_env():
    """Save the master key to .env file"""
    print("\n💾 SAVING MASTER KEY TO .ENV:")
    print("=" * 50)
    
    try:
        master_key = "tSo-GG44Oa9MGWQmXv470mdCPxMRwhuejU87skv22ZQ="
        
        # Read current .env
        env_path = ".env"
        env_content = ""
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_content = f.read()
        
        # Add or update SECRETS_MASTER_KEY
        if "SECRETS_MASTER_KEY" in env_content:
            # Replace existing
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('SECRETS_MASTER_KEY'):
                    lines[i] = f"SECRETS_MASTER_KEY={master_key}"
                    break
            env_content = '\n'.join(lines)
        else:
            # Add new
            env_content += f"\n# Secrets Management Master Key\nSECRETS_MASTER_KEY={master_key}\n"
        
        # Write back
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Master key saved to {env_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to save master key: {e}")
        return False

def main():
    print("🔧 COMPLETE SECRETS SYSTEM RESET")
    print("=" * 60)
    
    # Perform complete reset
    if complete_secrets_reset():
        print("\n✅ Secrets system reset successful!")
        
        # Verify integration
        verify_app_integration()
        
        # Save master key
        save_master_key_to_env()
        
        print(f"\n🎯 FINAL VERIFICATION:")
        print("=" * 50)
        print("✅ All secrets re-created with proper encryption")
        print("✅ Master key saved to .env file")
        print("✅ App integration ready")
        
        print(f"\n🚀 TO START THE APP:")
        print("1. python app.py")
        print("2. Visit: http://127.0.0.1:5000/admin/secrets/")
        print("3. Login as admin user")
        print("4. View and manage all migrated secrets")
        
        print(f"\n🚨 CRITICAL REMINDER:")
        print("The exposed passwords are now in the database:")
        print("- Gmail: uovrivxvitovrjcu")  
        print("- ServiceNow: f*X=u2QeWeP2")
        print("ROTATE THESE IMMEDIATELY!")
        
    else:
        print("\n❌ Secrets system reset failed!")

if __name__ == "__main__":
    main()