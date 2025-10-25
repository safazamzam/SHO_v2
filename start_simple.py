#!/usr/bin/env python3
"""
Simple script to start Flask app without debug mode for testing
"""

import os
import sys
sys.path.append('.')

from app import app

if __name__ == '__main__':
    # Run without debug mode to avoid auto-reloader issues
    app.run(host='127.0.0.1', port=5000, debug=False)