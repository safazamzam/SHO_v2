# -*- coding: utf-8 -*-
"""
Database migration to add secure secrets management tables
Run this to set up the hybrid secrets management system
"""

from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import sys

# Add the app directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import Config
    database_uri = Config.SQLALCHEMY_DATABASE_URI
except ImportError:
    # Fallback for direct execution
    database_uri = os.getenv('DATABASE_URL', 'sqlite:///shift_handover.db')

Base = declarative_base()

class SecretStore(Base):
    """Encrypted secret storage in database"""
    __tablename__ = 'secret_store'
    
    id = Column(Integer, primary_key=True)
    key_name = Column(String(255), unique=True, nullable=False, index=True)
    encrypted_value = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, default='application')
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    requires_restart = Column(Boolean, default=False, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    
    # Security fields
    last_accessed = Column(DateTime)
    access_count = Column(Integer, default=0)
    expires_at = Column(DateTime)  # For temporary secrets

class SecretAuditLog(Base):
    """Audit log for secret access and modifications"""
    __tablename__ = 'secret_audit_log'
    
    id = Column(Integer, primary_key=True)
    secret_key = Column(String(255), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # CREATE, READ, UPDATE, DELETE
    user_id = Column(String(255))
    user_email = Column(String(255))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    old_value_hash = Column(String(64))  # Hash of old value for comparison
    new_value_hash = Column(String(64))  # Hash of new value
    success = Column(Boolean, default=True)
    error_message = Column(Text)

def create_secrets_tables():
    """Create the secrets management tables"""
    print("🔐 Creating Secure Secrets Management Tables...")
    
    try:
        # Create engine
        engine = create_engine(database_uri)
        
        # Create tables
        Base.metadata.create_all(engine)
        
        print("✅ Successfully created secrets management tables:")
        print("   • secret_store - Encrypted secrets storage")
        print("   • secret_audit_log - Comprehensive audit logging")
        
        # Create session to add initial data
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Add some example secrets (these will be encrypted when using the secrets manager)
        example_secrets = [
            {
                'key_name': 'SERVICENOW_TIMEOUT',
                'category': 'application',
                'description': 'Timeout for ServiceNow API calls in seconds',
                'requires_restart': False
            },
            {
                'key_name': 'FEATURE_SERVICENOW_ENABLED',
                'category': 'feature',
                'description': 'Enable/disable ServiceNow integration',
                'requires_restart': True
            },
            {
                'key_name': 'EMAIL_SIGNATURE',
                'category': 'application',
                'description': 'Email signature for automated emails',
                'requires_restart': False
            }
        ]
        
        # Note: These are just placeholder entries - actual encrypted values will be set via the UI
        for secret_data in example_secrets:
            existing = session.query(SecretStore).filter_by(key_name=secret_data['key_name']).first()
            if not existing:
                secret = SecretStore(
                    key_name=secret_data['key_name'],
                    encrypted_value='[TO_BE_SET_VIA_UI]',  # Placeholder
                    category=secret_data['category'],
                    description=secret_data['description'],
                    requires_restart=secret_data['requires_restart'],
                    created_by='system',
                    is_active=False  # Inactive until properly configured
                )
                session.add(secret)
        
        session.commit()
        session.close()
        
        print("✅ Added example secret placeholders (to be configured via admin UI)")
        
        print("\n🚀 Next Steps:")
        print("1. Set SECRETS_MASTER_KEY environment variable")
        print("2. Initialize secrets manager in your app")
        print("3. Access /admin/secrets to configure secrets via UI")
        print("4. Configure your actual secret values")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating secrets tables: {e}")
        return False

def check_secrets_tables():
    """Check if secrets tables exist"""
    try:
        engine = create_engine(database_uri)
        
        # Try to query the tables
        with engine.connect() as conn:
            result = conn.execute("SELECT COUNT(*) FROM secret_store")
            secret_count = result.scalar()
            
            result = conn.execute("SELECT COUNT(*) FROM secret_audit_log")
            audit_count = result.scalar()
            
            print(f"✅ Secrets tables exist:")
            print(f"   • secret_store: {secret_count} secrets")
            print(f"   • secret_audit_log: {audit_count} audit entries")
            
            return True
            
    except Exception as e:
        print(f"❌ Secrets tables not found or error: {e}")
        return False

if __name__ == '__main__':
    print("🔐 Secrets Management Database Setup")
    print("=" * 50)
    
    # Check if tables already exist
    if check_secrets_tables():
        print("\n⚠️ Secrets tables already exist.")
        response = input("Do you want to recreate them? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
    
    # Create tables
    if create_secrets_tables():
        print("\n🎉 Secrets management setup completed successfully!")
        
        print("\n🔑 Security Checklist:")
        print("☐ Set SECRETS_MASTER_KEY environment variable")
        print("☐ Ensure database backups are encrypted")
        print("☐ Configure superadmin access for secrets UI")
        print("☐ Set up audit log monitoring")
        print("☐ Test secret encryption/decryption")
        
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1)