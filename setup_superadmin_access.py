#!/usr/bin/env python3
"""
🔍 CHECK USER ACCESS AND CREATE SUPERADMIN
Check current users and create/update superadmin for secrets access
"""

from app import app, db
from models.models import User, Account, Team
from werkzeug.security import generate_password_hash
import os

def check_existing_users():
    """Check what users exist in the system"""
    with app.app_context():
        print("👥 EXISTING USERS IN SYSTEM:")
        print("=" * 50)
        
        users = User.query.all()
        print(f"Total users: {len(users)}")
        
        for user in users:
            print(f"- Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Role: {user.role}")
            print(f"  Active: {user.is_active}")
            print(f"  Status: {user.status}")
            print(f"  Account ID: {user.account_id}")
            print(f"  Team ID: {user.team_id}")
            print("  ---")
        
        return users

def check_superadmin_access():
    """Check if any user has superadmin access"""
    with app.app_context():
        print("\n🔐 SUPERADMIN ACCESS CHECK:")
        print("=" * 50)
        
        # Check for super_admin role
        super_admins = User.query.filter_by(role='super_admin').all()
        print(f"Users with super_admin role: {len(super_admins)}")
        for user in super_admins:
            print(f"- {user.username} ({user.email})")
        
        # Check for specific admin emails
        admin_emails = ['mdsajid020@gmail.com', 'admin@yourcompany.com']
        email_admins = User.query.filter(User.email.in_(admin_emails)).all()
        print(f"Users with admin emails: {len(email_admins)}")
        for user in email_admins:
            print(f"- {user.username} ({user.email}) - Role: {user.role}")
        
        return super_admins + email_admins

def create_or_update_superadmin():
    """Create or update a superadmin user"""
    with app.app_context():
        print("\n🛠️ CREATING/UPDATING SUPERADMIN:")
        print("=" * 50)
        
        try:
            # First ensure we have basic account and team
            account = Account.query.first()
            if not account:
                account = Account(name='Default Account', status='active')
                db.session.add(account)
                db.session.commit()
                print("✅ Created default account")
            
            team = Team.query.first()
            if not team:
                team = Team(name='Admin Team', account_id=account.id, status='active')
                db.session.add(team)
                db.session.commit()
                print("✅ Created default team")
            
            # Check if admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            
            if admin_user:
                # Update existing user to superadmin
                admin_user.role = 'super_admin'
                admin_user.email = 'mdsajid020@gmail.com'  # Your email for additional access
                admin_user.is_active = True
                admin_user.status = 'active'
                admin_user.password = generate_password_hash('admin123')
                db.session.commit()
                print("✅ Updated existing admin user to super_admin")
                print(f"   Username: {admin_user.username}")
                print(f"   Email: {admin_user.email}")
                print(f"   Password: admin123")
                
            else:
                # Create new superadmin user
                admin_user = User(
                    username='admin',
                    email='mdsajid020@gmail.com',
                    password=generate_password_hash('admin123'),
                    role='super_admin',
                    is_active=True,
                    status='active',
                    account_id=account.id,
                    team_id=team.id,
                    first_name='Super',
                    last_name='Admin'
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Created new superadmin user")
                print(f"   Username: {admin_user.username}")
                print(f"   Email: {admin_user.email}")
                print(f"   Password: admin123")
            
            return admin_user
            
        except Exception as e:
            print(f"❌ Error creating superadmin: {e}")
            db.session.rollback()
            return None

def verify_secrets_access():
    """Verify that secrets access should work"""
    with app.app_context():
        print("\n🧪 VERIFYING SECRETS ACCESS:")
        print("=" * 50)
        
        # Check superadmin users
        admin_users = User.query.filter_by(role='super_admin').all()
        
        for user in admin_users:
            print(f"User: {user.username}")
            
            # Simulate the access check from the decorator
            is_superadmin = (
                hasattr(user, 'role') and user.role == 'super_admin'
            ) or (
                hasattr(user, 'email') and user.email in [
                    'mdsajid020@gmail.com',
                    'admin@yourcompany.com'
                ]
            )
            
            print(f"  Role check: {user.role == 'super_admin'}")
            print(f"  Email check: {user.email in ['mdsajid020@gmail.com', 'admin@yourcompany.com']}")
            print(f"  Overall access: {'✅ GRANTED' if is_superadmin else '❌ DENIED'}")

def main():
    print("🔍 USER ACCESS AND SUPERADMIN SETUP")
    print("=" * 60)
    
    # Check existing users
    users = check_existing_users()
    
    # Check superadmin access
    admin_users = check_superadmin_access()
    
    if not admin_users:
        print("\n⚠️ No superadmin users found. Creating one...")
        create_or_update_superadmin()
    else:
        print(f"\n✅ Found {len(admin_users)} admin user(s)")
    
    # Verify access
    verify_secrets_access()
    
    print(f"\n🚀 HOW TO ACCESS SECRETS DASHBOARD:")
    print("=" * 50)
    print("1. 🌐 Go to: http://127.0.0.1:5000/")
    print("2. 🔑 Login with:")
    print("   Username: admin")
    print("   Password: admin123")
    print("3. 🔐 Visit: http://127.0.0.1:5000/admin/secrets/")
    print("4. 👀 View all migrated secrets and passwords")
    print("5. 🔄 Rotate the exposed credentials immediately!")
    
    print(f"\n🚨 EXPOSED CREDENTIALS IN DATABASE:")
    print("- Gmail password: uovrivxvitovrjcu")
    print("- ServiceNow password: f*X=u2QeWeP2")
    print("THESE MUST BE ROTATED!")

if __name__ == "__main__":
    main()