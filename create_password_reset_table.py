#!/usr/bin/env python3
"""
Create password_reset_tokens table
"""

import sys
import os
sys.path.append('/app')

from app import app
from models.models import db

def create_password_reset_table():
    """Create password reset tokens table"""
    with app.app_context():
        try:
            print("🔧 Creating password_reset_tokens table...")
            
            # Create the table
            db.create_all()
            
            print("✅ password_reset_tokens table created successfully")
            
            # Check if table was created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'password_reset_tokens' in tables:
                print("✅ Table verification successful")
                
                # Show table structure
                columns = inspector.get_columns('password_reset_tokens')
                print(f"📋 Table structure ({len(columns)} columns):")
                for col in columns:
                    print(f"   - {col['name']}: {col['type']}")
            else:
                print("❌ Table verification failed")
                
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            return False
            
    return True

if __name__ == '__main__':
    create_password_reset_table()