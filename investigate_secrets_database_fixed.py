#!/usr/bin/env python3
"""
🔍 SECRETS DATABASE INVESTIGATION (Fixed for SQLAlchemy 2.x)
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
        
        # Check if secrets tables exist (SQLAlchemy 2.x compatible)
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%secret%';"
        with db.engine.connect() as connection:
            result = connection.execute(text(query))
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
            with db.engine.connect() as connection:
                result = connection.execute(text(query))
                secrets = result.fetchall()
            
            print(f"Secrets in database: {len(secrets)}")
            for secret in secrets:
                print(f"- {secret[0]} (Category: {secret[1]}, Active: {secret[2]}, Created: {secret[3]})")
                
        except Exception as e:
            print(f"Error querying secrets: {e}")

def check_all_tables():
    """Check all tables in the database"""
    with app.app_context():
        print("\n📋 ALL TABLES IN DATABASE:")
        print("=" * 50)
        
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        with db.engine.connect() as connection:
            result = connection.execute(text(query))
            tables = result.fetchall()
        
        print(f"Total tables: {len(tables)}")
        for table in tables:
            print(f"- {table[0]}")

def run_migration_properly():
    """Run the database migration properly"""
    print("\n🔧 RUNNING DATABASE MIGRATION:")
    print("=" * 50)
    
    try:
        # Import and run migration
        from migrations.create_secrets_tables import create_secrets_tables
        result = create_secrets_tables()
        if result:
            print("✅ Migration completed successfully")
            return True
        else:
            print("❌ Migration returned False")
            return False
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_missing_secrets():
    """Create the secrets that should have been migrated"""
    with app.app_context():
        print("\n🔧 CREATING MISSING SECRETS:")
        print("=" * 50)
        
        try:
            from models.secrets_manager import HybridSecretsManager
            
            # Set up master key
            master_key = os.environ.get('SECRETS_MASTER_KEY')
            if not master_key:
                from cryptography.fernet import Fernet
                master_key = Fernet.generate_key().decode()
                print(f"🔑 Generated SECRETS_MASTER_KEY: {master_key}")
                os.environ['SECRETS_MASTER_KEY'] = master_key
            
            secrets_manager = HybridSecretsManager(db.session, master_key)
            
            # Re-create the migrated secrets
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
            
            for key, value, category, description in secrets_to_create:
                result = secrets_manager.set_secret(key, value, category, description)
                print(f"{'✅' if result else '❌'} Created secret: {key}")
            
            print(f"\n✅ Created {len(secrets_to_create)} secrets")
            return True
            
        except Exception as e:
            print(f"❌ Error creating secrets: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    print("🔍 SECRETS DATABASE INVESTIGATION")
    print("=" * 60)
    
    # Check all tables first
    check_all_tables()
    
    # Check if tables exist
    tables_exist = check_database_tables()
    
    if not tables_exist:
        print("\n🔧 Tables don't exist. Running migration...")
        if run_migration_properly():
            tables_exist = check_database_tables()
    
    if tables_exist:
        check_secrets_data()
        
        # Create missing secrets if none found
        print("\n🔧 Creating missing secrets...")
        create_missing_secrets()
        
        # Check again
        check_secrets_data()
    
    print("\n📋 SUMMARY:")
    print("=" * 50)
    if tables_exist:
        print("✅ Database tables exist")
        print("💡 To access secrets UI:")
        print("   1. Start the app: python app.py")
        print("   2. Login as admin user")
        print("   3. Visit: http://127.0.0.1:5000/admin/secrets/")
        print("   4. Set SECRETS_MASTER_KEY environment variable")
    else:
        print("❌ Database tables missing - migration needed")

if __name__ == "__main__":
    main()