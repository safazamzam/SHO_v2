#!/usr/bin/env python3
"""
Debug API response to see actual secret data
"""
import requests

def debug_api():
    print("🔍 Debugging API Response...")
    
    session = requests.Session()
    
    # Login
    login_data = {'username': 'admin', 'password': 'admin123'}
    login_response = session.post('http://127.0.0.1:5000/login', data=login_data, allow_redirects=False)
    
    if login_response.status_code == 302:
        print("✅ Login successful")
        
        # Get API response
        api_response = session.get('http://127.0.0.1:5000/admin/secrets/api/secrets')
        if api_response.status_code == 200:
            data = api_response.json()
            print(f"✅ API Success: {data.get('success')}")
            print(f"✅ Number of secrets: {len(data.get('secrets', []))}")
            
            # Show detailed secrets
            secrets = data.get('secrets', [])
            print("\n📋 All secrets:")
            for i, secret in enumerate(secrets):
                print(f"  {i+1}. Key: '{secret.get('key_name')}' | Category: '{secret.get('category')}' | Description: '{secret.get('description', '')[:30]}...' | Status: {secret.get('is_active')}")
        else:
            print(f"❌ API failed: {api_response.status_code}")
    else:
        print(f"❌ Login failed: {login_response.status_code}")

if __name__ == "__main__":
    debug_api()