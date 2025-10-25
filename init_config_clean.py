#!/usr/bin/env python3
"""
Initialize Database Secrets (Unicode-safe)
This script initializes the database with encrypted secrets.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def initialize_secrets():
    """Initialize database secrets"""
    try:
        from app import create_app
        
        print("Initializing Database Secrets Management")
        print("=" * 45)
        
        app = create_app()
        
        with app.app_context():
            from services.secrets_service import init_secrets_manager, get_secrets_manager
            from models.database import db_session
            
            # Get master key for encryption
            master_key_file = 'secrets/secrets_master_key.txt'
            if os.path.exists(master_key_file):
                with open(master_key_file, 'r') as f:
                    master_key = f.read().strip()
                print(f"Master key loaded from {master_key_file}")
            else:
                print(f"ERROR: Master key file not found: {master_key_file}")
                return False
            
            # Initialize secrets manager
            try:
                secrets_manager = init_secrets_manager(db_session(), master_key)
                print("Secrets manager initialized successfully")
            except Exception as e:
                print(f"Error initializing secrets manager: {e}")
                return False
            
            # Read secrets from .env backup if available
            env_backup_file = '.env.backup.20251023_120651'
            if os.path.exists(env_backup_file):
                print(f"Loading secrets from {env_backup_file}")
                
                # Read environment variables
                env_vars = {}
                with open(env_backup_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip().strip('"\'')
                
                # Define secrets to migrate
                secrets_mapping = {
                    'SMTP_SERVER': env_vars.get('SMTP_SERVER', 'smtp.gmail.com'),
                    'SMTP_PORT': env_vars.get('SMTP_PORT', '587'),
                    'SMTP_USERNAME': env_vars.get('SMTP_USERNAME', ''),
                    'SMTP_PASSWORD': env_vars.get('SMTP_PASSWORD', ''),
                    'SERVICENOW_INSTANCE': env_vars.get('SERVICENOW_INSTANCE', ''),
                    'SERVICENOW_USERNAME': env_vars.get('SERVICENOW_USERNAME', ''),
                    'SERVICENOW_PASSWORD': env_vars.get('SERVICENOW_PASSWORD', ''),
                    'FLASK_SECRET_KEY': env_vars.get('SECRET_KEY', ''),
                    'ENCRYPTION_KEY': env_vars.get('ENCRYPTION_KEY', ''),
                    'SSO_CLIENT_ID': env_vars.get('SSO_CLIENT_ID', ''),
                    'SSO_CLIENT_SECRET': env_vars.get('SSO_CLIENT_SECRET', ''),
                    'SSO_DISCOVERY_URL': env_vars.get('SSO_DISCOVERY_URL', ''),
                    'SSO_REDIRECT_URI': env_vars.get('SSO_REDIRECT_URI', ''),
                    'DEBUG_MODE': env_vars.get('DEBUG', 'False')
                }
                
                # Store secrets
                stored_count = 0
                for secret_name, secret_value in secrets_mapping.items():
                    if secret_value:
                        try:
                            secrets_manager.set_secret(secret_name, secret_value, 'Application')
                            print(f"Stored: {secret_name}")
                            stored_count += 1
                        except Exception as e:
                            print(f"Error storing {secret_name}: {e}")
                    else:
                        print(f"Skipped: {secret_name} (empty value)")
                
                print(f"\nStored {stored_count} secrets successfully")
                return True
            else:
                print(f"WARNING: Environment backup file not found: {env_backup_file}")
                return False
                
    except Exception as e:
        print(f"Error during initialization: {e}")
        return False

if __name__ == "__main__":
    success = initialize_secrets()
    if success:
        print("SUCCESS: Database secrets initialized!")
        sys.exit(0)
    else:
        print("FAILED: Database initialization failed!")
        sys.exit(1)