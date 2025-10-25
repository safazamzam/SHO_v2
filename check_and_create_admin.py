#!/usr/bin/env python3
"""
Initialize or check admin user in database
"""
from models.models import User, Account, Team
from app import app
from werkzeug.security import generate_password_hash, check_password_hash

with app.app_context():
    print("🔍 Checking database users...")
    
    # List all users
    users = User.query.all()
    print(f"Total users in database: {len(users)}")
    
    for user in users:
        print(f"  - {user.username} (Role: {user.role}, Account: {user.account_id}, Team: {user.team_id})")
    
    # Check if admin user exists
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        print(f"\n✅ Admin user found:")
        print(f"   Username: {admin_user.username}")
        print(f"   Role: {admin_user.role}")
        print(f"   Account ID: {admin_user.account_id}")
        print(f"   Team ID: {admin_user.team_id}")
        
        # Test password
        test_password = 'admin123'
        if check_password_hash(admin_user.password, test_password):
            print(f"   ✅ Password '{test_password}' matches")
        else:
            print(f"   ❌ Password '{test_password}' does not match")
            print(f"   Password hash: {admin_user.password[:50]}...")
    else:
        print("\n❌ No admin user found. Creating one...")
        
        # Create a super admin user
        admin_user = User(
            username='admin',
            password=generate_password_hash('admin123'),
            role='super_admin',
            account_id=None,
            team_id=None
        )
        
        from extensions import db
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Super admin user created with username='admin', password='admin123'")
    
    # List all accounts and teams for context
    accounts = Account.query.all()
    print(f"\nAccounts in database: {len(accounts)}")
    for account in accounts:
        print(f"  - {account.id}: {account.name}")
    
    teams = Team.query.all()
    print(f"\nTeams in database: {len(teams)}")
    for team in teams:
        print(f"  - {team.id}: {team.name} (Account: {team.account_id})")