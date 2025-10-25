"""
Simple migration script to create secrets management tables
"""

import sqlite3
import os
from datetime import datetime

def create_secrets_tables():
    """Create the secrets management tables in SQLite"""
    print("🔐 Creating Secrets Management Tables...")
    
    # Use the same database as your app
    db_path = "shift_handover.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create secret_store table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS secret_store (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_name VARCHAR(255) UNIQUE NOT NULL,
                encrypted_value TEXT NOT NULL,
                category VARCHAR(50) NOT NULL DEFAULT 'application',
                description TEXT,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                requires_restart BOOLEAN NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR(255),
                updated_by VARCHAR(255),
                last_accessed DATETIME,
                access_count INTEGER DEFAULT 0,
                expires_at DATETIME
            )
        ''')
        
        # Create index on key_name
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_secret_store_key_name ON secret_store(key_name)')
        
        # Create secret_audit_log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS secret_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                secret_key VARCHAR(255) NOT NULL,
                action VARCHAR(50) NOT NULL,
                user_id VARCHAR(255),
                user_email VARCHAR(255),
                ip_address VARCHAR(45),
                user_agent TEXT,
                timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                old_value_hash VARCHAR(64),
                new_value_hash VARCHAR(64),
                success BOOLEAN NOT NULL DEFAULT 1,
                error_message TEXT
            )
        ''')
        
        # Create index on secret_key and timestamp
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_secret_key ON secret_audit_log(secret_key)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON secret_audit_log(timestamp)')
        
        # Add some example placeholder secrets
        example_secrets = [
            ('SERVICENOW_TIMEOUT', '[TO_BE_SET_VIA_UI]', 'application', 'Timeout for ServiceNow API calls in seconds', 0, 0),
            ('FEATURE_SERVICENOW_ENABLED', '[TO_BE_SET_VIA_UI]', 'feature', 'Enable/disable ServiceNow integration', 0, 1),
            ('EMAIL_SIGNATURE', '[TO_BE_SET_VIA_UI]', 'application', 'Email signature for automated emails', 0, 0),
            ('SMTP_USERNAME', '[TO_BE_SET_VIA_UI]', 'external', 'SMTP username for email sending', 0, 0),
            ('SMTP_PASSWORD', '[TO_BE_SET_VIA_UI]', 'external', 'SMTP password for email sending', 0, 0)
        ]
        
        for secret_data in example_secrets:
            cursor.execute('''
                INSERT OR IGNORE INTO secret_store 
                (key_name, encrypted_value, category, description, is_active, requires_restart, created_by)
                VALUES (?, ?, ?, ?, ?, ?, 'system')
            ''', secret_data)
        
        conn.commit()
        conn.close()
        
        print("✅ Successfully created secrets management tables:")
        print("   • secret_store - Encrypted secrets storage")
        print("   • secret_audit_log - Comprehensive audit logging")
        print("✅ Added example secret placeholders (to be configured via admin UI)")
        
        print("\n🚀 Next Steps:")
        print("1. Set SECRETS_MASTER_KEY environment variable")
        print("2. Initialize secrets manager in your app")
        print("3. Access /admin/secrets to configure secrets via UI")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating secrets tables: {e}")
        return False

if __name__ == '__main__':
    print("🔐 Secrets Management Database Setup")
    print("=" * 50)
    
    if create_secrets_tables():
        print("\n🎉 Secrets management setup completed successfully!")
        print("\n🔑 Security Checklist:")
        print("☐ Set SECRETS_MASTER_KEY environment variable")
        print("☐ Integrate with Flask app")
        print("☐ Configure superadmin access")
        print("☐ Test secret encryption/decryption")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")