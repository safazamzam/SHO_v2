#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.models import db, SecretStore
from config import Config
from app import app

# Check what ServiceNow secrets exist in database
print("Checking ServiceNow secrets in database...")

with app.app_context():
    # Get all secrets
    all_secrets = SecretStore.query.all()
    
    print("All secrets in database:")
    for secret in all_secrets:
        print(f"  {secret.key_name} = {secret.encrypted_value[:20]}..." if len(secret.encrypted_value) > 20 else f"  {secret.key_name} = {secret.encrypted_value}")
    
    print("\nLooking for ServiceNow related secrets:")
    servicenow_secrets = SecretStore.query.filter(SecretStore.key_name.like('%SERVICENOW%')).all()
    
    if servicenow_secrets:
        for secret in servicenow_secrets:
            print(f"  Found: {secret.key_name} = {secret.encrypted_value}")
    else:
        print("  No ServiceNow secrets found!")
        
    # Also check for any secrets that might be similar
    print("\nAll secret keys:")
    for secret in all_secrets:
        print(f"  - {secret.key_name}")