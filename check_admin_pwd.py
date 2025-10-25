#!/usr/bin/env python3

from models.models import User, db
from app import app
from werkzeug.security import check_password_hash

def check_admin_credentials():
    with app.app_context():
        admin_user = User.query.filter_by(email='admin@acme.com').first()
        
        if admin_user:
            print(f"Admin user found: {admin_user.email}")
            print(f"Role: {admin_user.role}")
            
            # Try common passwords
            common_passwords = ['admin', 'password', 'admin123', '123456', 'test', 'acme']
            
            for pwd in common_passwords:
                if check_password_hash(admin_user.password, pwd):
                    print(f"✅ Password found: {pwd}")
                    return
            
            print("❌ Could not determine password with common passwords")
            print("Try: admin, password, admin123, 123456, test, acme")
        else:
            print("No admin user found")

if __name__ == '__main__':
    check_admin_credentials()