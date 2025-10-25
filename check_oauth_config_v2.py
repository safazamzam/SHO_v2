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
        # Check OAuth configuration using the new model structure
        oauth_configs = SSOConfig.query.filter_by(provider_type='oauth').all()
        
        if oauth_configs:
            print('✅ OAuth Configuration Found:')
            config_dict = {}
            enabled_configs = []
            
            for config in oauth_configs:
                config_dict[config.config_key] = config.config_value
                if config.enabled:
                    enabled_configs.append(config)
                    
            print(f'Total OAuth configs: {len(oauth_configs)}')
            print(f'Enabled OAuth configs: {len(enabled_configs)}')
            
            # Display configuration
            for key, value in config_dict.items():
                if 'secret' in key.lower() or 'password' in key.lower():
                    print(f'{key}: ****** (encrypted)')
                else:
                    print(f'{key}: {value}')
                    
            # Check if OAuth is enabled
            oauth_enabled = SSOConfig.is_provider_enabled('oauth')
            print(f'\n📋 OAuth Provider Status: {"✅ ENABLED" if oauth_enabled else "❌ DISABLED"}')
            
            # Get full configuration using the helper method
            if oauth_enabled:
                full_config = SSOConfig.get_provider_config('oauth')
                print(f'\n🔧 Active OAuth Configuration:')
                for key, value in full_config.items():
                    if 'secret' in key.lower() or 'password' in key.lower():
                        print(f'  {key}: ****** (decrypted)')
                    else:
                        print(f'  {key}: {value}')
        else:
            print('❌ No OAuth configuration found in database')
            
        # Check all SSO configs
        all_configs = SSOConfig.query.all()
        print(f'\n📋 Total SSO configs in database: {len(all_configs)}')
        
        providers = {}
        for config in all_configs:
            if config.provider_type not in providers:
                providers[config.provider_type] = {'enabled': False, 'count': 0}
            providers[config.provider_type]['count'] += 1
            if config.enabled:
                providers[config.provider_type]['enabled'] = True
                
        for provider_type, info in providers.items():
            status = "✅ ENABLED" if info['enabled'] else "❌ DISABLED"
            print(f'- {provider_type}: {status} ({info["count"]} configs)')
            
    except Exception as e:
        print(f'❌ Error checking configuration: {e}')
        import traceback
        traceback.print_exc()