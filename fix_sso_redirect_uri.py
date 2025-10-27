#!/usr/bin/env python3
"""
Fix SSO Redirect URI for nginx Reverse Proxy Setup

This script updates the SSO redirect URIs from port 5000 to port 80 (nginx proxy)
to fix SSO authentication after enabling nginx reverse proxy.
"""

import os
import sys
sys.path.append('.')

from app import create_app
from models.sso_config import SSOConfig
from models.models import db

def fix_sso_redirect_uris():
    """Fix SSO redirect URIs for nginx proxy setup"""
    
    app = create_app()
    
    with app.app_context():
        print("🔧 Fixing SSO Redirect URIs for nginx proxy...")
        
        # Get all SSO configurations
        sso_configs = SSOConfig.query.filter_by(config_key='redirect_uri').all()
        
        if not sso_configs:
            print("❌ No SSO redirect URIs found in database")
            return False
        
        updated_count = 0
        
        for config in sso_configs:
            old_uri = config.config_value
            print(f"\n📋 Processing {config.provider_type} ({config.provider_name})")
            print(f"   Current URI: {old_uri}")
            
            # Check if URI contains :5000 (direct Flask access)
            if ':5000' in old_uri:
                # Update to use port 80 (nginx proxy)
                new_uri = old_uri.replace(':5000', '')
                config.config_value = new_uri
                
                print(f"   ✅ Updated to: {new_uri}")
                updated_count += 1
            elif 'localhost:5000' in old_uri:
                # Update localhost:5000 to IP address
                new_uri = old_uri.replace('localhost:5000', '35.200.202.18')
                config.config_value = new_uri
                
                print(f"   ✅ Updated to: {new_uri}")
                updated_count += 1
            else:
                print(f"   ℹ️  No update needed")
        
        if updated_count > 0:
            try:
                db.session.commit()
                print(f"\n✅ Successfully updated {updated_count} redirect URIs")
                
                # Show all current redirect URIs
                print(f"\n📋 Current SSO Redirect URIs:")
                updated_configs = SSOConfig.query.filter_by(config_key='redirect_uri').all()
                for config in updated_configs:
                    print(f"   {config.provider_type}: {config.config_value}")
                
                return True
            except Exception as e:
                print(f"❌ Error saving changes: {e}")
                db.session.rollback()
                return False
        else:
            print("\nℹ️  No redirect URIs needed updating")
            return True

def show_current_config():
    """Show current SSO configuration"""
    app = create_app()
    
    with app.app_context():
        print("📋 Current SSO Configuration:")
        
        # Get all SSO configurations
        providers = SSOConfig.query.filter_by(enabled=True).all()
        
        if not providers:
            print("❌ No enabled SSO providers found")
            return
        
        current_provider = None
        for config in providers:
            if config.provider_name != current_provider:
                print(f"\n🔐 {config.provider_name} ({config.provider_type})")
                current_provider = config.provider_name
            
            if config.encrypted:
                value = "***encrypted***" if config.config_key in ['client_secret'] else SSOConfig._decrypt_value(config.config_value)
            else:
                value = config.config_value
            
            print(f"   {config.config_key}: {value}")

def main():
    print("🚀 SSO Redirect URI Fix Tool")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--show':
        show_current_config()
        return
    
    print("This tool will update SSO redirect URIs from port 5000 to port 80")
    print("to fix SSO authentication after enabling nginx reverse proxy.\n")
    
    # Show current configuration
    show_current_config()
    
    print("\n" + "=" * 50)
    response = input("Do you want to update the redirect URIs? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        success = fix_sso_redirect_uris()
        if success:
            print("\n🎉 SSO redirect URIs updated successfully!")
            print("\n📝 Next steps:")
            print("1. Update Google OAuth console with new redirect URI")
            print("2. Restart the application: docker-compose -f docker-compose.prod.yml restart web")
            print("3. Test SSO login: http://35.200.202.18/login")
        else:
            print("\n❌ Failed to update redirect URIs")
    else:
        print("\n❌ Operation cancelled")

if __name__ == '__main__':
    main()