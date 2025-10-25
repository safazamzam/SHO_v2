#!/usr/bin/env python3
"""
Cleanup expired password reset tokens
"""

import sys
sys.path.append('/app')

from app import app
from services.password_reset_service import PasswordResetService

def cleanup_expired_tokens():
    """Clean up expired password reset tokens"""
    with app.app_context():
        print("🧹 Cleaning up expired password reset tokens...")
        
        try:
            count = PasswordResetService.cleanup_expired_tokens()
            print(f"✅ Cleaned up {count} expired tokens")
            return True
        except Exception as e:
            print(f"❌ Error cleaning up tokens: {e}")
            return False

if __name__ == '__main__':
    cleanup_expired_tokens()