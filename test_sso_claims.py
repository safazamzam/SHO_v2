#!/usr/bin/env python3
"""
SSO Claims Testing Script
Use this to test SSO login and view all claims being received from the OAuth server
"""

from app import app
import logging

def setup_detailed_logging():
    """Configure detailed logging for SSO testing"""
    
    # Set up console logging with detailed format
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('sso_claims_debug.log')
        ]
    )
    
    # Set Flask app logger to INFO level
    app.logger.setLevel(logging.INFO)
    
    print("=" * 80)
    print("🔍 SSO CLAIMS TESTING MODE ACTIVATED")
    print("=" * 80)
    print("📝 Detailed SSO claims logging is now enabled")
    print("📄 Logs will be saved to: sso_claims_debug.log")
    print("🌐 Navigate to: http://127.0.0.1:5000")
    print("🔐 Perform SSO login to see detailed claims analysis")
    print("=" * 80)
    
if __name__ == '__main__':
    setup_detailed_logging()
    
    # Run Flask app with debug mode
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )