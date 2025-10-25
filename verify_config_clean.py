#!/usr/bin/env python3
"""
Verify Secrets Configuration Script (Unicode-safe)
This script verifies that all secrets are properly configured and accessible.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_secrets_access():
    """Test if secrets can be accessed properly"""
    try:
        from app import create_app
        
        print("Database Secrets Configuration Verification")
        print("=" * 55)
        
        app = create_app()
        
        with app.app_context():
            from services.secrets_service import get_secrets_manager
            
            secrets_manager = get_secrets_manager()
            if not secrets_manager:
                print("ERROR: Secrets manager not initialized")
                return False
            
            # Test critical secrets
            critical_secrets = [
                'SMTP_SERVER',
                'SMTP_PORT', 
                'SMTP_USERNAME',
                'SMTP_PASSWORD',
                'SERVICENOW_INSTANCE',
                'SERVICENOW_USERNAME',
                'SERVICENOW_PASSWORD',
                'FLASK_SECRET_KEY',
                'ENCRYPTION_KEY',
                'SSO_CLIENT_ID',
                'SSO_CLIENT_SECRET',
                'SSO_DISCOVERY_URL',
                'SSO_REDIRECT_URI',
                'DEBUG_MODE'
            ]
            
            accessible_count = 0
            missing_count = 0
            
            print("\nTesting individual secrets:")
            print("-" * 30)
            
            for secret_name in critical_secrets:
                try:
                    value = secrets_manager.get_secret(secret_name)
                    if value is not None and value.strip():
                        # Mask sensitive values for display
                        if any(keyword in secret_name.lower() for keyword in ['password', 'secret', 'key']):
                            display_value = '*' * min(len(str(value)), 8)
                        else:
                            display_value = str(value)[:20] + ('...' if len(str(value)) > 20 else '')
                        
                        print(f"PASS {secret_name}: {display_value}")
                        accessible_count += 1
                    else:
                        print(f"FAIL {secret_name}: NOT FOUND")
                        missing_count += 1
                except Exception as e:
                    print(f"ERROR {secret_name}: {e}")
                    missing_count += 1
            
            print(f"\nSummary:")
            print(f"   Accessible: {accessible_count}")
            print(f"   Missing: {missing_count}")
            
            if missing_count == 0:
                print(f"\nAll secrets are properly configured!")
                return True
            else:
                print(f"\n{missing_count} secrets are missing or inaccessible")
                return False
                
    except Exception as e:
        print(f"Error during verification: {e}")
        return False

if __name__ == "__main__":
    success = test_secrets_access()
    if success:
        print("SUCCESS: Configuration verification completed!")
        sys.exit(0)
    else:
        print("FAILED: Configuration verification failed!")
        sys.exit(1)