#!/usr/bin/env python3
"""
Update SSO User Profile for Testing
Manually update an SSO user's profile to test the template display
"""

import os
import sys
sys.path.append('.')

from models.models import db, User
from app import app

def update_sso_user_profile():
    """Update SSO user profile for testing"""
    
    with app.app_context():
        print("🔧 UPDATING SSO USER PROFILE FOR TESTING")
        print("=" * 50)
        
        # Find users who might be SSO users (empty password)
        sso_users = User.query.filter_by(password='').all()
        
        if not sso_users:
            print("❌ No SSO users found (users with empty passwords)")
            # Let's check all users
            all_users = User.query.all()
            print(f"📊 Found {len(all_users)} total users:")
            for user in all_users:
                print(f"  👤 {user.email} - Password: {'SET' if user.password else 'EMPTY'}")
            return
        
        print(f"📊 Found {len(sso_users)} SSO users:")
        
        for i, user in enumerate(sso_users):
            print(f"\n{i+1}. 👤 {user.email}")
            print(f"   Current first_name: {user.first_name}")
            print(f"   Current last_name: {user.last_name}")
            print(f"   Current profile_picture: {user.profile_picture}")
            
            # Update with test data
            user.first_name = "Sajid"
            user.last_name = "Mohammad" 
            user.profile_picture = "https://ui-avatars.com/api/?name=Sajid+Mohammad&background=2d3748&color=fff&size=128"
            
            print(f"   ✅ Updated to: {user.first_name} {user.last_name}")
            print(f"   ✅ Profile picture: {user.profile_picture}")
        
        # Save changes
        db.session.commit()
        print("\n✅ Successfully updated SSO user profiles!")
        
        # Verify the display_name property works
        for user in sso_users:
            print(f"👤 {user.email} - Display Name: '{user.display_name}'")

if __name__ == '__main__':
    update_sso_user_profile()