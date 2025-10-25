#!/usr/bin/env python3
"""
Create a superadmin user for testing the secrets management system
"""
import os
import sys
from werkzeug.security import generate_password_hash

# Set the master key before importing the app
os.environ['SECRETS_MASTER_KEY'] = 'Ll8LcS_EcS8zn1XfecvQVjAcT1Hf_O74uLmfYnXHr3k='

from app import app
from models.models import db, User

def create_superadmin():
    """Create a superadmin user for testing"""
    try:
        with app.app_context():
            # Check if superadmin already exists
            existing_admin = User.query.filter_by(role='super_admin').first()
            
            if existing_admin:
                print("✅ Superadmin user already exists!")
                print(f"   Username: {existing_admin.username}")
                print(f"   Email: {existing_admin.email}")
                print(f"   Role: {existing_admin.role}")
                print("\n🔐 You can access the secrets management interface at:")
                print("   http://127.0.0.1:5000/admin/secrets")
                print("\n💡 Try logging in with the existing admin credentials.")
                return
            
            # Create superadmin user
            admin_user = User(
                username='admin',
                email='admin@example.com',
                role='super_admin',  # This is the key - super_admin role
                password=generate_password_hash('admin123'),
                is_active=True,
                account_id=1,  # Assuming account 1 exists
                team_id=1  # Assuming team 1 exists
            )
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("🎉 Superadmin user created successfully!")
            print("   Email: admin@example.com")
            print("   Password: admin123")
            print("   Role: super_admin")
            print("\n🔐 You can now access the secrets management interface at:")
            print("   http://127.0.0.1:5000/admin/secrets")
            
    except Exception as e:
        print(f"❌ Error creating superadmin: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_superadmin()