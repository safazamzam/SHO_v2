#!/usr/bin/env python3
"""
🔍 SECRETS DATABASE INVESTIGATION
Check the current state of secrets in the database
"""

from app import app, db
from sqlalchemy import text
import os

def check_database_tables():
    """Check what tables exist in the database"""
    with app.app_context():
        print("🔍 CHECKING DATABASE TABLES:")
        print("=" * 50)
        
        # Check if secrets tables exist
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%secret%';"
        result = db.engine.execute(text(query))
        tables = result.fetchall()
        
        print(f"Secret-related tables found: {len(tables)}")
        for table in tables:
            print(f"- {table[0]}")
        
        if not tables:
            print("❌ No secrets tables found in database!")
            print("The migration may not have been run properly.")
            return False
        
        return True

def check_secrets_data():
    """Check what secrets are actually stored"""
    with app.app_context():
        print("\n🔐 CHECKING SECRETS DATA:")
        print("=" * 50)
        
        try:
            # Check secrets in secret_store table
            query = "SELECT key_name, category, is_active, created_at FROM secret_store LIMIT 20;"
            result = db.engine.execute(text(query))
            secrets = result.fetchall()
            
            print(f"Secrets in database: {len(secrets)}")
            for secret in secrets:
                print(f"- {secret[0]} (Category: {secret[1]}, Active: {secret[2]}, Created: {secret[3]})")
                
        except Exception as e:
            print(f"Error querying secrets: {e}")

def check_secrets_manager():
    """Check if secrets manager can access the secrets"""
    with app.app_context():
        print("\n🛠️ CHECKING SECRETS MANAGER:")
        print("=" * 50)
        
        try:
            from models.secrets_manager import HybridSecretsManager
            
            # Initialize secrets manager
            master_key = os.environ.get('SECRETS_MASTER_KEY')
            if not master_key:
                print("⚠️ No SECRETS_MASTER_KEY found in environment")
                return
            
            secrets_manager = HybridSecretsManager(db.session, master_key)
            
            # List secrets through the manager
            secrets_list = secrets_manager.list_secrets(include_values=False)
            
            print(f"Secrets manager found {len(secrets_list)} secrets:")
            for secret in secrets_list:
                print(f"- {secret['key_name']} (Category: {secret['category']}, Active: {secret['is_active']})")
                
        except Exception as e:
            print(f"Error with secrets manager: {e}")

def run_database_migration():
    """Run the database migration if tables don't exist"""
    print("\n🔧 RUNNING DATABASE MIGRATION:")
    print("=" * 50)
    
    try:
        from migrations.create_secrets_tables import create_secrets_tables
        create_secrets_tables()
        print("✅ Migration completed successfully")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    print("🔍 SECRETS DATABASE INVESTIGATION")
    print("=" * 60)
    
    # Check if tables exist
    tables_exist = check_database_tables()
    
    if not tables_exist:
        print("\n🔧 Tables don't exist. Running migration...")
        if run_database_migration():
            tables_exist = check_database_tables()
    
    if tables_exist:
        check_secrets_data()
        check_secrets_manager()
    
    print("\n📋 SUMMARY:")
    print("=" * 50)
    if tables_exist:
        print("✅ Database tables exist")
        print("💡 If secrets UI is empty, the issue may be:")
        print("   1. SECRETS_MASTER_KEY not set in environment")
        print("   2. Secrets manager not properly initialized in app")
        print("   3. Admin user permissions not configured")
        print("   4. UI not loading secrets from database")
    else:
        print("❌ Database tables missing - migration needed")

if __name__ == "__main__":
    main()