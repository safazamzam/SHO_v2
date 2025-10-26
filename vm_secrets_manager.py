"""
Simplified secrets manager for VM deployment
"""

import os
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class SecretsManager:
    """Simple secrets manager for backward compatibility"""
    
    def __init__(self):
        self.initialized = False
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.initialized = True
        logger.info("✅ Secrets manager initialized (simplified mode)")
    
    def get_secret(self, key_name, default=None):
        """Get secret value - fallback to environment variables"""
        # Try environment variable first
        env_value = os.getenv(key_name, default)
        if env_value:
            return env_value
        
        # Try uppercase version
        env_value = os.getenv(key_name.upper(), default)
        if env_value:
            return env_value
            
        return default
    
    def is_configured(self):
        """Check if secrets manager is configured"""
        return self.initialized

# Global instances
secrets_manager = SecretsManager()

def init_secrets_manager(app):
    """Initialize secrets manager with Flask app"""
    secrets_manager.init_app(app)
    return secrets_manager