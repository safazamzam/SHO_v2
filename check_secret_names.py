#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, SecretStore
from config import Config
from app import app

# Check what ServiceNow secrets exist in database
print("Checking ServiceNow secrets in database...")

with app.app_context():
    # Get all secrets
    all_secrets = SecretStore.query.all()
    
    print("All secrets in database:")
    for secret in all_secrets:
        print(f"  {secret.key} = {secret.value[:10]}..." if len(secret.value) > 10 else f"  {secret.key} = {secret.value}")
    
    print("\nLooking for ServiceNow related secrets:")
    servicenow_secrets = SecretStore.query.filter(SecretStore.key.like('%SERVICENOW%')).all()
    
    for secret in servicenow_secrets:
        print(f"  Found: {secret.key} = {secret.value}")