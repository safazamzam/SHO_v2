#!/usr/bin/env python3
"""
Debug SSO User Profile Data
Check what profile data is stored in the database for SSO users
"""

import os
import sys
sys.path.append('.')

from models.models import db, User
from app import app

def debug_user_profile():
    """Debug user profile data in database"""
    
    with app.app_context():
        print("🔍 SSO USER PROFILE DEBUG")
        print("=" * 50)
        
        # Get all users
        users = User.query.all()
        
        if not users:
            print("❌ No users found in database")
            return
        
        print(f"📊 Found {len(users)} users in database:")
        print()
        
        for user in users:
            print(f"👤 USER: {user.email}")
            print(f"  🔖 Username: {user.username}")
            print(f"  📧 Email: {user.email}")
            print(f"  🏷️ First Name: {user.first_name}")
            print(f"  🏷️ Last Name: {user.last_name}")
            print(f"  📝 Display Name: {user.display_name}")
            print(f"  🖼️ Profile Picture: {user.profile_picture}")
            print(f"  🛡️ Role: {user.role}")
            print(f"  ✅ Active: {user.is_active}")
            print(f"  📊 Status: {user.status}")
            print("-" * 40)

if __name__ == '__main__':
    debug_user_profile()