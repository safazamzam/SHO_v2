#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

# Set database URL for direct connection
os.environ['DATABASE_URL'] = 'mysql://root:root@localhost:3306/shift_handover'

from models.sso_config import SSOConfig
from models.models import db
from app import app
import json

with app.app_context():
    try:
        # Check OAuth configuration
        oauth_config = SSOConfig.query.filter_by(provider_type='oauth').first()
        if oauth_config:
            config_data = json.loads(oauth_config.config_data)
            print('✅ OAuth Configuration Found:')
            print(f'Client ID: {config_data.get("client_id")}')
            print(f'Client Secret: {"***" if config_data.get("client_secret") else "Not set"}')
            print(f'Authorization URL: {config_data.get("authorization_url")}')
            print(f'Token URL: {config_data.get("token_url")}')
            print(f'User Info URL: {config_data.get("user_info_url")}')
            print(f'Redirect URI: {config_data.get("redirect_uri")}')
            print(f'Enabled: {oauth_config.is_enabled}')
            print(f'Account ID: {oauth_config.account_id}')
            print(f'Created: {oauth_config.created_at}')
            print(f'Updated: {oauth_config.updated_at}')
        else:
            print('❌ No OAuth configuration found in database')
            
        # Check all SSO configs
        all_configs = SSOConfig.query.all()
        print(f'\n📋 Total SSO configs in database: {len(all_configs)}')
        for config in all_configs:
            print(f'- {config.provider_type}: Enabled={config.is_enabled}, Account={config.account_id}')
            
    except Exception as e:
        print(f'❌ Error checking configuration: {e}')
        import traceback
        traceback.print_exc()