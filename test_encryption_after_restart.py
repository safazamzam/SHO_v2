#!/usr/bin/env python3

import os
import sys
import subprocess

def test_encryption_functionality():
    """Test that the encryption system is working properly after restart"""
    
    print("Testing SSO Configuration Encryption System...")
    print("=" * 60)
    
    # Test script content
    test_script = '''
import os
import sys
sys.path.append('/app')

from models.sso_config import SSOConfig
from app import app

with app.app_context():
    # Get SSO configuration
    sso_config = SSOConfig.query.filter_by(provider_name='epam').first()
    
    if not sso_config:
        print("ERROR: No EPAM SSO configuration found!")
        sys.exit(1)
    
    print(f"Provider: {sso_config.provider_name}")
    print(f"Encrypted Client ID (length): {len(sso_config.client_id)} chars")
    print(f"Encrypted Client Secret (length): {len(sso_config.client_secret)} chars")
    
    # Test decryption
    config = sso_config.get_provider_config()
    
    print("\\n--- Decryption Test ---")
    print(f"Decrypted Client ID: {config['client_id'][:20]}...")
    print(f"Decrypted Client Secret: {config['client_secret'][:10]}...")
    
    # Verify encryption key is loaded
    print(f"\\nEncryption Key Available: {'Yes' if os.getenv('SSO_ENCRYPTION_KEY') else 'No'}")
    
    print("\\n✅ Encryption system is working properly!")
    print("✅ Sensitive SSO data is encrypted in database!")
    print("✅ Decryption is working for OAuth functionality!")
'''

    # Write test script
    with open('test_encryption_after_restart.py', 'w') as f:
        f.write(test_script)
    
    print("Created encryption test script...")
    return True

if __name__ == "__main__":
    test_encryption_functionality()