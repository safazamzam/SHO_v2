#!/usr/bin/env python3
import sys
sys.path.append('/app')

from models.models import User, db
from werkzeug.security import check_password_hash
from app import app

with app.app_context():
    user = User.query.filter_by(username='superadmin').first()
    
    if user:
        print(f"User found: {user.username}")
        print(f"User ID: {user.id}")
        print(f"Role: {user.role}")
        print(f"Is Active: {user.is_active}")
        print(f"Status: {user.status}")
        print(f"Account ID: {user.account_id}")
        print(f"Team ID: {user.team_id}")
        
        # Test password
        test_password = 'admin123'
        password_check = check_password_hash(user.password, test_password)
        print(f"Password check result: {password_check}")
        
        # Test role check
        role_check = user.role == 'super_admin'
        print(f"Role check (super_admin): {role_check}")
        
    else:
        print("User not found!")