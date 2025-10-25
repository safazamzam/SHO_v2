#!/usr/bin/env python3
import sys
sys.path.append('/app')

from models.sso_config import SSOConfig
from models.models import db
from app import app
import base64

def fix_client_secret():
    with app.app_context():
        try:
            # Find the OAuth client_secret configuration
            secret_config = SSOConfig.query.filter_by(
                provider_type='oauth',
                config_key='client_secret'
            ).first()
            
            if secret_config:
                print(f"Found client secret config:")
                print(f"  Encrypted: {secret_config.encrypted}")
                print(f"  Value length: {len(secret_config.config_value)}")
                print(f"  Value starts with: {secret_config.config_value[:10]}")
                
                if secret_config.encrypted:
                    print("⚠️ Client secret is encrypted but decryption is failing")
                    print("🔧 Converting to plaintext to fix OAuth authentication...")
                    
                    # Set to plaintext for now to fix OAuth
                    # Get the actual client secret from user
                    actual_secret = input("Please enter the actual client secret: ").strip()
                    
                    if actual_secret:
                        secret_config.config_value = actual_secret
                        secret_config.encrypted = False
                        db.session.commit()
                        print("✅ Client secret updated to plaintext successfully")
                        print(f"✅ New value length: {len(actual_secret)}")
                    else:
                        print("❌ No client secret provided")
                else:
                    print(f"✅ Client secret is already plaintext: {secret_config.config_value[:10]}...")
            else:
                print("❌ No client secret configuration found")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    fix_client_secret()