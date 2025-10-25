#!/usr/bin/env python3

"""
Simple test to check if our enhanced secrets page is working
"""

from app import app

def test_secrets_page():
    with app.app_context():
        try:
            # Start test client
            client = app.test_client()
            
            # Try to access the page without login first
            print("Testing secrets page access...")
            response = client.get('/admin/secrets/', follow_redirects=False)
            print(f"Without login - Status: {response.status_code}")
            
            if response.status_code == 302:
                print(f"Redirected to: {response.location}")
            
            # Try with basic auth context
            with client.session_transaction() as sess:
                sess['user_id'] = 1  # Simulate logged in user
                sess['_fresh'] = True
            
            response = client.get('/admin/secrets/')
            print(f"With session - Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Page loads successfully")
                print(f"Response length: {len(response.data)} bytes")
            else:
                print(f"❌ Page failed to load: {response.status_code}")
                print(f"Response data preview: {response.data[:500]}")
                
        except Exception as e:
            print(f"❌ Error testing page: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_secrets_page()