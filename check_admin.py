#!/usr/bin/env python3
"""
Check admin user details
"""
from models.models import User
from app import app

with app.app_context():
    user = User.query.filter_by(username='admin').first()
    if user:
        print(f"User: {user.username}")
        print(f"Role: {user.role}")
        print(f"Account ID: {user.account_id}")
        print(f"Team ID: {user.team_id}")
    else:
        print("Admin user not found")