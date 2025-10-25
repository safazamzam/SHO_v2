#!/usr/bin/env python3
"""
Quick test of enhanced secrets page v2
"""
import requests

def quick_test():
    print("🧪 Testing Enhanced Secrets Dashboard v2...")
    
    session = requests.Session()
    
    # Login
    login_data = {'username': 'admin', 'password': 'admin123'}
    login_response = session.post('http://127.0.0.1:5000/login', data=login_data, allow_redirects=False)
    
    if login_response.status_code == 302:
        print("✅ Login successful")
        
        # Test secrets page
        secrets_response = session.get('http://127.0.0.1:5000/admin/secrets')
        if secrets_response.status_code == 200:
            print("✅ Secrets page accessible")
            
            # Check for enhanced v2 features
            content = secrets_response.text
            checks = {
                'Enhanced Secrets Management': 'Enhanced title',
                'Enterprise-grade security': 'Enhanced subtitle',
                'Last Updated': 'Enhanced statistics',
                'Quick Actions': 'Quick action buttons',
                'Comprehensive configuration': 'Enhanced description'
            }
            
            print("\n📋 Enhanced Features Detection:")
            for text, feature in checks.items():
                if text in content:
                    print(f"   ✅ {feature}: Found")
                else:
                    print(f"   ❌ {feature}: Not found")
        else:
            print(f"❌ Secrets page failed: {secrets_response.status_code}")
    else:
        print(f"❌ Login failed: {login_response.status_code}")

if __name__ == "__main__":
    quick_test()