#!/usr/bin/env python3
import sqlite3

def check_tables():
    """Check what tables exist in the database"""
    try:
        conn = sqlite3.connect('shift_handover.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📋 Database Tables:")
        for table in tables:
            print(f"  ✅ {table[0]}")
            
        # Check if our secrets tables exist
        secrets_tables = ['secret_store', 'secret_audit_log']
        existing_table_names = [table[0] for table in tables]
        
        print("\n🔐 Secrets Management Tables:")
        for secrets_table in secrets_tables:
            if secrets_table in existing_table_names:
                print(f"  ✅ {secrets_table} - EXISTS")
            else:
                print(f"  ❌ {secrets_table} - MISSING")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

if __name__ == "__main__":
    check_tables()