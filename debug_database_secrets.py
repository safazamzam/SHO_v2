#!/usr/bin/env python3
"""
Check secrets directly from database
"""
from models.models import SecretStore
from app import app

with app.app_context():
    print("🔍 Checking secrets in database...")
    
    secrets = SecretStore.query.all()
    print(f"Total secrets: {len(secrets)}")
    
    for i, secret in enumerate(secrets):
        print(f"  {i+1}. Key: '{secret.key_name}' | Category: '{secret.category}' | Value: '{secret.encrypted_value[:20] if secret.encrypted_value else None}...' | Active: {secret.is_active}")