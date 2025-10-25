#!/usr/bin/env python3
"""
Reset admin password to admin123
"""
from models.models import User, db
from app import app
from werkzeug.security import generate_password_hash

with app.app_context():
    print("🔧 Resetting admin password...")
    
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        admin_user.password = generate_password_hash('admin123')
        db.session.commit()
        print("✅ Admin password reset to 'admin123'")
        print(f"   Role: {admin_user.role}")
        print(f"   Account ID: {admin_user.account_id}")
        print(f"   Team ID: {admin_user.team_id}")
    else:
        print("❌ Admin user not found")