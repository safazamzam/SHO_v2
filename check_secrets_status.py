#!/usr/bin/env python3
from app import app, db
from sqlalchemy import text

with app.app_context():
    print("CURRENT SECRETS IN DATABASE:")
    print("=" * 60)
    result = db.session.execute(text('SELECT key_name, category, is_active, description FROM secret_store ORDER BY category, key_name;'))
    secrets = result.fetchall()
    
    current_category = ""
    for row in secrets:
        key_name, category, is_active, description = row
        
        if category != current_category:
            print(f"\n📂 {category.upper()}:")
            current_category = category
        
        status = "✅ Active" if is_active else "❌ Inactive"
        print(f"   {key_name:<25} | {status} | {description}")
    
    print(f"\n📊 SUMMARY: {len(secrets)} total secrets")