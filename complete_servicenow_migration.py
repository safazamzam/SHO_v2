#!/usr/bin/env python3
"""
Complete the ServiceNow secrets migration
"""

import os
import sys
sys.path.append('.')

def complete_servicenow_migration():
    """Complete the ServiceNow secrets migration"""
    print("🔧 COMPLETING SERVICENOW SECRETS MIGRATION")
    print("=" * 50)
    
    try:
        from app import app, db
        from models.secrets_manager import HybridSecretsManager
        
        with app.app_context():
            # Initialize secrets manager
            secrets_manager = HybridSecretsManager(db.session)
            
            # ServiceNow credentials from environment
            servicenow_instance = os.environ.get('SERVICENOW_INSTANCE', '')
            servicenow_username = os.environ.get('SERVICENOW_USERNAME', '')
            servicenow_password = os.environ.get('SERVICENOW_PASSWORD', '')
            
            servicenow_secrets = [
                ('SERVICENOW_INSTANCE', servicenow_instance, 'ServiceNow instance URL', 'ServiceNow'),
                ('SERVICENOW_USERNAME', servicenow_username, 'ServiceNow integration username', 'ServiceNow'),
                ('SERVICENOW_PASSWORD', servicenow_password, 'ServiceNow integration password (migrated from environment)', 'ServiceNow')
            ]
            
            for key, value, description, category in servicenow_secrets:
                if value and value != '[TO_BE_CONFIGURED]':
                    try:
                        result = secrets_manager.set_secret(
                            key_name=key,
                            value=value,
                            description=description,
                            category=category
                        )
                        if result['success']:
                            print(f"   ✅ Migrated {key}: {value[:10]}..." if 'PASSWORD' not in key else f"   ✅ Migrated {key}: [HIDDEN]")
                        else:
                            print(f"   ⚠️ Failed to migrate {key}: {result.get('error', 'Unknown error')}")
                    except Exception as e:
                        print(f"   ❌ Error migrating {key}: {e}")
                else:
                    print(f"   ⚠️ No value found for {key}")
            
            print("\n✅ ServiceNow migration completed!")
            print("🔍 You can verify in the secrets dashboard: http://127.0.0.1:5000/admin/secrets/")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    complete_servicenow_migration()