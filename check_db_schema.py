#!/usr/bin/env python3
from app import app, db
from sqlalchemy import text

with app.app_context():
    print("🔍 DATABASE SCHEMA CHECK:")
    print("=" * 40)
    
    # Check secret_store table structure
    result = db.session.execute(text('PRAGMA table_info(secret_store);'))
    columns = result.fetchall()
    
    print("secret_store table columns:")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
    
    print(f"\n📊 Sample data:")
    result = db.session.execute(text('SELECT * FROM secret_store LIMIT 2;'))
    rows = result.fetchall()
    for row in rows:
        print(f"- {row}")