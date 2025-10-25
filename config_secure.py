"""
Production Security Configuration Manager
This module handles secure credential management for production deployment
"""

import os
import json
import base64
from cryptography.fernet import Fernet
from typing import Dict, Any, Optional
import logging

class SecureConfigManager:
    """
    Secure configuration manager that handles credentials safely
    Supports multiple backends: Environment Variables, Docker Secrets, Azure Key Vault
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Initialize encryption for sensitive data
        if encryption_key:
            self.fernet = Fernet(encryption_key.encode())
        else:
            # Generate or load encryption key
            key = os.environ.get('ENCRYPTION_KEY')
            if not key:
                key = Fernet.generate_key().decode()
                self.logger.warning("Generated new encryption key - store this securely!")
                print(f"🔑 ENCRYPTION_KEY={key}")
            self.fernet = Fernet(key.encode())
    
    def get_secret(self, secret_name: str, default: Any = None, required: bool = False) -> Any:
        """
        Get secret from multiple sources in priority order:
        1. Docker Secrets (files in /run/secrets/)
        2. Environment Variables
        3. Default value
        """
        # Try Docker Secrets first
        secret_file = f"/run/secrets/{secret_name.lower()}"
        if os.path.exists(secret_file):
            try:
                with open(secret_file, 'r') as f:
                    value = f.read().strip()
                    self.logger.info(f"✅ Loaded {secret_name} from Docker secret")
                    return value
            except Exception as e:
                self.logger.error(f"Error reading Docker secret {secret_name}: {e}")
        
        # Try environment variables
        env_value = os.environ.get(secret_name.upper())
        if env_value:
            self.logger.info(f"✅ Loaded {secret_name} from environment variable")
            return env_value
        
        # Try with alternative naming conventions
        alt_names = [
            secret_name.replace('_', '-'),
            secret_name.replace('-', '_'),
            f"FLASK_{secret_name}",
            f"APP_{secret_name}"
        ]
        
        for alt_name in alt_names:
            env_value = os.environ.get(alt_name.upper())
            if env_value:
                self.logger.info(f"✅ Loaded {secret_name} from environment variable {alt_name}")
                return env_value
        
        # Return default or raise error
        if required and default is None:
            raise ValueError(f"Required secret '{secret_name}' not found in any source")
        
        if default is not None:
            self.logger.warning(f"⚠️ Using default value for {secret_name}")
            return default
        
        self.logger.warning(f"⚠️ Secret {secret_name} not found, returning None")
        return None
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt a sensitive value"""
        if not value:
            return value
        encrypted = self.fernet.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a sensitive value"""
        if not encrypted_value:
            return encrypted_value
        try:
            decoded = base64.b64decode(encrypted_value.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            return encrypted_value
    
    def validate_configuration(self) -> Dict[str, bool]:
        """Validate that all required configuration is present"""
        required_configs = {
            'SECRET_KEY': self.get_secret('SECRET_KEY'),
            'DATABASE_URL': self.get_secret('DATABASE_URL'),
            'SSO_ENCRYPTION_KEY': self.get_secret('SSO_ENCRYPTION_KEY'),
        }
        
        optional_configs = {
            'SMTP_USERNAME': self.get_secret('SMTP_USERNAME'),
            'SMTP_PASSWORD': self.get_secret('SMTP_PASSWORD'),
            'SERVICENOW_INSTANCE': self.get_secret('SERVICENOW_INSTANCE'),
            'SERVICENOW_USERNAME': self.get_secret('SERVICENOW_USERNAME'),
            'SERVICENOW_PASSWORD': self.get_secret('SERVICENOW_PASSWORD'),
            'GOOGLE_OAUTH_CLIENT_ID': self.get_secret('GOOGLE_OAUTH_CLIENT_ID'),
            'GOOGLE_OAUTH_CLIENT_SECRET': self.get_secret('GOOGLE_OAUTH_CLIENT_SECRET'),
        }
        
        validation_results = {}
        
        # Check required configs
        for key, value in required_configs.items():
            validation_results[key] = bool(value)
            if not value:
                self.logger.error(f"❌ Required configuration missing: {key}")
            else:
                self.logger.info(f"✅ Required configuration present: {key}")
        
        # Check optional configs
        for key, value in optional_configs.items():
            validation_results[key] = bool(value)
            if not value:
                self.logger.warning(f"⚠️ Optional configuration missing: {key}")
            else:
                self.logger.info(f"✅ Optional configuration present: {key}")
        
        return validation_results

# Global instance
config_manager = SecureConfigManager()

class ProductionConfig:
    """Production configuration using secure credential management"""
    
    # Core Flask settings
    SECRET_KEY = config_manager.get_secret('SECRET_KEY', required=True)
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    
    # Database configuration
    DATABASE_URL = config_manager.get_secret('DATABASE_URL', required=True)
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {"sslmode": "require"} if DATABASE_URL and 'postgres' in DATABASE_URL else {}
    }
    
    # Email configuration
    MAIL_SERVER = config_manager.get_secret('SMTP_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(config_manager.get_secret('SMTP_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = config_manager.get_secret('SMTP_USERNAME')
    MAIL_PASSWORD = config_manager.get_secret('SMTP_PASSWORD')
    MAIL_DEFAULT_SENDER = config_manager.get_secret('TEAM_EMAIL', MAIL_USERNAME)
    TEAM_EMAIL = config_manager.get_secret('TEAM_EMAIL', MAIL_USERNAME)
    
    # ServiceNow configuration
    SERVICENOW_INSTANCE = config_manager.get_secret('SERVICENOW_INSTANCE')
    SERVICENOW_USERNAME = config_manager.get_secret('SERVICENOW_USERNAME')
    SERVICENOW_PASSWORD = config_manager.get_secret('SERVICENOW_PASSWORD')
    SERVICENOW_TIMEOUT = int(config_manager.get_secret('SERVICENOW_TIMEOUT', 30))
    SERVICENOW_ASSIGNMENT_GROUPS = config_manager.get_secret('SERVICENOW_ASSIGNMENT_GROUPS', '')
    
    # SSO configuration
    GOOGLE_OAUTH_CLIENT_ID = config_manager.get_secret('GOOGLE_OAUTH_CLIENT_ID')
    GOOGLE_OAUTH_CLIENT_SECRET = config_manager.get_secret('GOOGLE_OAUTH_CLIENT_SECRET')
    SSO_ENCRYPTION_KEY = config_manager.get_secret('SSO_ENCRYPTION_KEY', required=True)
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # HTTPS enforcement
    PREFERRED_URL_SCHEME = 'https'
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        return config_manager.validate_configuration()

if __name__ == '__main__':
    # Test configuration
    print("🔐 Testing Production Configuration...")
    validation = ProductionConfig.validate()
    
    required_configs = ['SECRET_KEY', 'DATABASE_URL', 'SSO_ENCRYPTION_KEY']
    missing_required = [k for k in required_configs if not validation.get(k)]
    
    if missing_required:
        print(f"❌ Missing required configurations: {missing_required}")
        print("Please set the required environment variables or Docker secrets")
    else:
        print("✅ All required configurations are present")
        print("🚀 Production configuration is ready!")