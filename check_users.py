#!/usr/bin/env python3

from models.models import User, db
from app import app

def check_users():
    with app.app_context():
        users = User.query.all()
        print(f'Total users: {len(users)}')
        
        for user in users[:10]:  # Show first 10 users
            role = getattr(user, 'role', 'No role')
            print(f'User: {user.email}, Role: {role}')
            
        # Check if there's a superadmin
        super_admins = User.query.filter_by(role='super_admin').all()
        print(f'\nSuper admins found: {len(super_admins)}')
        
        for admin in super_admins:
            print(f'Super admin: {admin.email}')

if __name__ == '__main__':
    check_users()