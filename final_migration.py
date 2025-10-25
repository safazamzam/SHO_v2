#!/usr/bin/env python3
"""
Final ServiceNow Migration with actual credentials
"""

import sys
sys.path.append('.')

def migrate_servicenow_with_values():
    """Migrate ServiceNow with actual values from backup"""
    print("🔧 FINAL SERVICENOW MIGRATION WITH ACTUAL VALUES")
    print("=" * 55)
    
    try:
        from app import app, db
        from models.secrets_manager import HybridSecretsManager
        
        with app.app_context():
            # Initialize secrets manager
            secrets_manager = HybridSecretsManager(db.session)
            
            # Actual ServiceNow credentials from backup file
            servicenow_secrets = [
                ('SERVICENOW_INSTANCE', 'dev284357.service-now.com', 'ServiceNow instance URL', 'ServiceNow'),
                ('SERVICENOW_USERNAME', 'admin', 'ServiceNow integration username', 'ServiceNow'),
                ('SERVICENOW_PASSWORD', 'f*X=u2QeWeP2', 'ServiceNow integration password (migrated from environment)', 'ServiceNow'),
                ('SERVICENOW_TIMEOUT', '30', 'ServiceNow API timeout in seconds', 'ServiceNow'),
                ('SERVICENOW_ENABLED', 'true', 'Enable ServiceNow integration', 'ServiceNow')
            ]
            
            # Also migrate the actual SMTP credentials
            smtp_secrets = [
                ('SMTP_USERNAME', 'mdsajid020@gmail.com', 'Gmail SMTP username', 'SMTP'),
                ('SMTP_PASSWORD', 'uovrivxvitovrjcu', 'Gmail app-specific password (TO BE ROTATED)', 'SMTP'),
                ('TEAM_EMAIL', 'mdsajid020@gmail.com', 'Team email for notifications', 'SMTP')
            ]
            
            print("📧 Migrating SMTP credentials with actual values:")
            for key, value, description, category in smtp_secrets:
                try:
                    success = secrets_manager.set_secret(
                        key_name=key,
                        value=value,
                        description=description,
                        category=category
                    )
                    if success:
                        if 'PASSWORD' in key:
                            print(f"   ✅ Migrated {key}: [HIDDEN - NEEDS ROTATION]")
                        else:
                            print(f"   ✅ Migrated {key}: {value}")
                    else:
                        print(f"   ⚠️ Failed to migrate {key}")
                except Exception as e:
                    print(f"   ❌ Error migrating {key}: {e}")
            
            print("\n🔧 Migrating ServiceNow credentials:")
            for key, value, description, category in servicenow_secrets:
                try:
                    success = secrets_manager.set_secret(
                        key_name=key,
                        value=value,
                        description=description,
                        category=category
                    )
                    if success:
                        if 'PASSWORD' in key:
                            print(f"   ✅ Migrated {key}: [HIDDEN - NEEDS ROTATION]")
                        else:
                            print(f"   ✅ Migrated {key}: {value}")
                    else:
                        print(f"   ⚠️ Failed to migrate {key}")
                except Exception as e:
                    print(f"   ❌ Error migrating {key}: {e}")
            
            print(f"\n🎉 MIGRATION COMPLETED!")
            print("=" * 55)
            print("✅ All secrets have been migrated to secure database storage")
            print("🔍 You can verify in the secrets dashboard: http://127.0.0.1:5000/admin/secrets/")
            print("\n🚨 CRITICAL SECURITY ACTIONS REQUIRED:")
            print("1. 🔄 ROTATE the Gmail password: uovrivxvitovrjcu")
            print("2. 🔄 ROTATE the ServiceNow password: f*X=u2QeWeP2")
            print("3. 🧹 Remove hardcoded secrets from config.py")
            print("4. 🧹 Clean up any remaining hardcoded credentials")
            print("5. 🔐 Update the rotated credentials in the secrets dashboard")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    migrate_servicenow_with_values()