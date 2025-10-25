#!/usr/bin/env python3
"""
Script to initialize SMTP configuration table and default values
"""

import os
import sys
from flask import Flask

# Add the app directory to Python path
sys.path.append('/app')

from models.models import db
from models.smtp_config import SMTPConfig

def init_smtp_config():
    """Initialize SMTP configuration table and default values"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:secure_root_password_2023!@db/shift_handover'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        try:
            # Create table if it doesn't exist
            db.create_all()
            print("✅ Database tables created/verified")
            
            # Initialize default SMTP configurations
            result = SMTPConfig.initialize_default_configs()
            if result:
                print("✅ SMTP default configurations initialized")
            else:
                print("❌ Failed to initialize SMTP default configurations")
                
            # Check if table exists and show current configs
            configs = SMTPConfig.get_all_configs()
            print(f"📊 Current SMTP configurations: {len(configs)} entries")
            for key, value in configs.items():
                display_value = "••••••••" if 'password' in key.lower() else value
                print(f"  - {key}: {display_value}")
                
        except Exception as e:
            print(f"❌ Error initializing SMTP config: {e}")
            return False
            
    return True

if __name__ == '__main__':
    init_smtp_config()