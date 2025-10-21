#!/usr/bin/env python3
import sys
sys.path.append('/app')

from models.sso_config import SSOConfig
from models.models import db
from app import app
import os

def fix_sso_encryption():
    with app.app_context():
        try:
            # Set a persistent encryption key to avoid regeneration
            # This should be set as an environment variable in production
            encryption_key = "your-persistent-32-char-key-here123456"  # 32 characters
            os.environ['SSO_ENCRYPTION_KEY'] = encryption_key
            
            print("🔐 Setting up SSO encryption security...")
            
            # Find all OAuth configurations that should be encrypted
            sensitive_keys = ['client_secret', 'client_id']
            
            for key in sensitive_keys:
                config = SSOConfig.query.filter_by(
                    provider_type='oauth',
                    config_key=key
                ).first()
                
                if config:
                    current_value = config.config_value
                    
                    if key == 'client_secret':
                        # Make sure client secret is the correct value
                        if len(current_value) == 32 and current_value.startswith('No42d'):
                            print(f"✅ {key}: Using correct plaintext value")
                            # Encrypt it
                            config.encrypted = True
                            config.save()
                            print(f"🔐 {key}: Now encrypted")
                        else:
                            print(f"⚠️ {key}: Unexpected value length {len(current_value)}")
                            
                    elif key == 'client_id':
                        # Client ID can be encrypted too but less critical
                        print(f"✅ {key}: {current_value}")
                        config.encrypted = True
                        config.save()
                        print(f"🔐 {key}: Now encrypted")
                        
                else:
                    print(f"❌ {key}: Configuration not found")
            
            # Verify encryption works
            print("\n🔍 Verifying encryption/decryption works...")
            oauth_config = SSOConfig.get_provider_config('oauth')
            
            if oauth_config.get('client_secret'):
                print(f"✅ Client secret decrypted successfully (length: {len(oauth_config.get('client_secret'))})")
            else:
                print("❌ Client secret decryption failed")
                
            if oauth_config.get('client_id'):
                print(f"✅ Client ID decrypted successfully: {oauth_config.get('client_id')}")
            else:
                print("❌ Client ID decryption failed")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    fix_sso_encryption()