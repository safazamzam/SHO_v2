#!/usr/bin/env python3
"""
Check admin credentials and reset if needed
"""
from models.models import User, db
from app import app
from werkzeug.security import generate_password_hash, check_password_hash

with app.app_context():
    print("🔍 Checking admin user credentials...")
    
    # Find admin user
    admin_user = User.query.filter_by(username='admin').first()
    
    if admin_user:
        print(f"\n✅ Admin user found:")
        print(f"   Username: {admin_user.username}")
        print(f"   Role: {admin_user.role}")
        print(f"   Account ID: {admin_user.account_id}")
        print(f"   Team ID: {admin_user.team_id}")
        
        # Test the password we set earlier
        test_password = 'admin123'
        if check_password_hash(admin_user.password, test_password):
            print(f"\n✅ CORRECT CREDENTIALS:")
            print(f"   Username: admin")
            print(f"   Password: admin123")
        else:
            print(f"\n❌ Password 'admin123' doesn't work. Resetting...")
            admin_user.password = generate_password_hash('admin123')
            db.session.commit()
            print(f"✅ Password reset! New credentials:")
            print(f"   Username: admin")
            print(f"   Password: admin123")
    else:
        print("\n❌ No admin user found. Creating one...")
        admin_user = User(
            username='admin',
            password=generate_password_hash('admin123'),
            role='super_admin',
            account_id=1,
            team_id=1
        )
        db.session.add(admin_user)
        db.session.commit()
        print(f"✅ Admin user created:")
        print(f"   Username: admin")
        print(f"   Password: admin123")
    
    print(f"\n🌐 Login URL: http://127.0.0.1:5000/login")
    print(f"🔐 Secrets Dashboard: http://127.0.0.1:5000/admin/secrets")