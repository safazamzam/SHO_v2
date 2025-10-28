#!/usr/bin/env python3
"""
Simple SSO Redirect URI Updater
Updates SSO redirect URIs for nginx proxy setup
"""

import sqlite3
import os

def update_redirect_uris_sqlite():
    """Update redirect URIs in SQLite database"""
    
    # Check for SQLite database
    db_files = ['shift_handover.db', 'instance/shift_handover.db', 'database/shift_handover.db']
    db_path = None
    
    for path in db_files:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ No SQLite database found")
        return False
    
    print(f"📋 Using database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if sso_config table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='sso_config'
        """)
        
        if not cursor.fetchone():
            print("❌ sso_config table not found")
            return False
        
        # Get current redirect URIs
        cursor.execute("""
            SELECT id, provider_type, provider_name, config_value 
            FROM sso_config 
            WHERE config_key = 'redirect_uri'
        """)
        
        configs = cursor.fetchall()
        
        if not configs:
            print("❌ No redirect URIs found in database")
            return False
        
        print("\n📋 Current redirect URIs:")
        for config in configs:
            print(f"   {config[1]} ({config[2]}): {config[3]}")
        
        # Ask for confirmation
        print(f"\n🔧 This will update redirect URIs:")
        print(f"   Remove :5000 port from URLs")
        print(f"   Change localhost to 35.200.202.18")
        
        response = input("Continue? (y/N): ")
        
        if response.lower() not in ['y', 'yes']:
            print("❌ Operation cancelled")
            return False
        
        # Update redirect URIs
        updated_count = 0
        
        for config in configs:
            config_id, provider_type, provider_name, old_uri = config
            new_uri = old_uri
            
            # Remove :5000 port
            if ':5000' in new_uri:
                new_uri = new_uri.replace(':5000', '')
                updated_count += 1
            
            # Replace localhost with IP
            if 'localhost' in new_uri:
                new_uri = new_uri.replace('localhost', '35.200.202.18')
                updated_count += 1
            
            if new_uri != old_uri:
                cursor.execute("""
                    UPDATE sso_config 
                    SET config_value = ? 
                    WHERE id = ?
                """, (new_uri, config_id))
                
                print(f"   ✅ Updated {provider_type}: {old_uri} → {new_uri}")
        
        if updated_count > 0:
            conn.commit()
            print(f"\n✅ Successfully updated {updated_count} redirect URIs")
        else:
            print("\nℹ️  No updates needed")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_current_config():
    """Show current redirect URIs"""
    
    db_files = ['shift_handover.db', 'instance/shift_handover.db', 'database/shift_handover.db']
    db_path = None
    
    for path in db_files:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ No SQLite database found")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT provider_type, provider_name, config_key, config_value 
            FROM sso_config 
            WHERE enabled = 1
            ORDER BY provider_name, config_key
        """)
        
        configs = cursor.fetchall()
        
        if not configs:
            print("❌ No SSO configurations found")
            return
        
        print(f"📋 Current SSO Configuration (from {db_path}):")
        current_provider = None
        
        for config in configs:
            provider_type, provider_name, config_key, config_value = config
            
            if provider_name != current_provider:
                print(f"\n🔐 {provider_name} ({provider_type})")
                current_provider = provider_name
            
            # Hide sensitive values
            if config_key in ['client_secret']:
                value = "***hidden***"
            else:
                value = config_value
            
            print(f"   {config_key}: {value}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")

def main():
    print("🔧 SSO Redirect URI Update Tool")
    print("=" * 40)
    
    # Show current configuration
    show_current_config()
    
    print("\n" + "=" * 40)
    print("This will update redirect URIs for nginx proxy (port 80)")
    
    if update_redirect_uris_sqlite():
        print("\n🎉 Redirect URIs updated successfully!")
        print("\n📝 Next steps:")
        print("1. Update your organization's OAuth console with new redirect URI")
        print("2. Test SSO login: http://35.200.202.18/login")
    else:
        print("\n❌ Failed to update redirect URIs")

if __name__ == '__main__':
    main()