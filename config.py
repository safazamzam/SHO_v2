import os
import logging
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Load environment variables from .env file
load_dotenv()

class SecureConfigManager:
    """Secure configuration manager for handling sensitive credentials"""
    
    @staticmethod
    def get_secret(secret_name, default=None, required=False):
        """
        Get secret from multiple sources in priority order:
        1. Docker Secrets (files in /run/secrets/)
        2. Environment Variables
        3. Default value
        """
        # Try Docker Secrets first (production)
        secret_file = f"/run/secrets/{secret_name.lower()}"
        if os.path.exists(secret_file):
            try:
                with open(secret_file, 'r') as f:
                    value = f.read().strip()
                    logging.info(f"✅ Loaded {secret_name} from Docker secret")
                    return value
            except Exception as e:
                logging.error(f"Error reading Docker secret {secret_name}: {e}")
        
        # Try environment variables
        env_value = os.environ.get(secret_name.upper())
        if env_value:
            logging.info(f"✅ Loaded {secret_name} from environment variable")
            return env_value
        
        # Try alternative naming conventions
        alt_names = [
            secret_name.replace('_', '-'),
            secret_name.replace('-', '_'),
            f"FLASK_{secret_name}",
            f"APP_{secret_name}"
        ]
        
        for alt_name in alt_names:
            env_value = os.environ.get(alt_name.upper())
            if env_value:
                logging.info(f"✅ Loaded {secret_name} from environment variable {alt_name}")
                return env_value
        
        # Return default or raise error
        if required and default is None:
            raise ValueError(f"❌ Required secret '{secret_name}' not found in any source")
        
        if default is not None:
            if secret_name.lower() in ['password', 'key', 'secret']:
                logging.warning(f"⚠️ Using default value for sensitive config: {secret_name}")
            else:
                logging.info(f"✅ Using default value for {secret_name}")
            return default
        
        logging.warning(f"⚠️ Secret {secret_name} not found, returning None")
        return None

# Initialize secure config manager
secure_config = SecureConfigManager()

class Config:
    """Base configuration class with secure credential handling"""
    
    # Core Flask settings - NEVER use weak defaults in production
    SECRET_KEY = secure_config.get_secret('SECRET_KEY')
    if not SECRET_KEY:
        # Generate a strong key if none provided
        SECRET_KEY = Fernet.generate_key().decode()
        print(f"🔑 Generated SECRET_KEY: {SECRET_KEY}")
        print("⚠️ Please set SECRET_KEY environment variable for production!")
    
    # Database configuration with secure fallbacks
    DATABASE_URL = secure_config.get_secret('DATABASE_URL')
    if not DATABASE_URL:
        # Use secure SQLite for development only
        DATABASE_URL = 'sqlite:///shift_handover.db'
        print("⚠️ Using SQLite for development. Set DATABASE_URL for production!")
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Email configuration with security warnings
    MAIL_SERVER = secure_config.get_secret('SMTP_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(secure_config.get_secret('SMTP_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    
    # Get email credentials securely
    MAIL_USERNAME = secure_config.get_secret('SMTP_USERNAME')
    MAIL_PASSWORD = secure_config.get_secret('SMTP_PASSWORD')
    
    # Security check for email credentials
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print("⚠️ Email credentials not configured. Email features will be disabled.")
        MAIL_USERNAME = None
        MAIL_PASSWORD = None
    elif MAIL_PASSWORD == '*** MIGRATED TO DATABASE - ROTATE IMMEDIATELY ***':  # Your exposed password
        print("🚨 SECURITY ALERT: Default Gmail password detected!")
        print("Please update SMTP_PASSWORD environment variable immediately!")
    
    MAIL_DEFAULT_SENDER = secure_config.get_secret('TEAM_EMAIL', MAIL_USERNAME)
    TEAM_EMAIL = secure_config.get_secret('TEAM_EMAIL', MAIL_USERNAME)
    
    # ServiceNow Integration Configuration
    SERVICENOW_INSTANCE = secure_config.get_secret('SERVICENOW_INSTANCE')
    SERVICENOW_USERNAME = secure_config.get_secret('SERVICENOW_USERNAME')
    SERVICENOW_PASSWORD = secure_config.get_secret('SERVICENOW_PASSWORD')
    SERVICENOW_API_VERSION = secure_config.get_secret('SERVICENOW_API_VERSION', 'v1')
    SERVICENOW_TIMEOUT = int(secure_config.get_secret('SERVICENOW_TIMEOUT', 30))
    SERVICENOW_ENABLED = secure_config.get_secret('SERVICENOW_ENABLED', 'false').lower() == 'true'
    SERVICENOW_ASSIGNMENT_GROUPS = secure_config.get_secret('SERVICENOW_ASSIGNMENT_GROUPS', '')
    
    # SSO Configuration
    SSO_ENCRYPTION_KEY = secure_config.get_secret('SSO_ENCRYPTION_KEY')
    if not SSO_ENCRYPTION_KEY:
        SSO_ENCRYPTION_KEY = Fernet.generate_key().decode()
        print(f"🔑 Generated SSO_ENCRYPTION_KEY: {SSO_ENCRYPTION_KEY}")
        print("⚠️ Please set SSO_ENCRYPTION_KEY environment variable for production!")
    
    # Google OAuth Configuration
    GOOGLE_OAUTH_CLIENT_ID = secure_config.get_secret('GOOGLE_OAUTH_CLIENT_ID')
    GOOGLE_OAUTH_CLIENT_SECRET = secure_config.get_secret('GOOGLE_OAUTH_CLIENT_SECRET')
    
    # Security settings
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    @classmethod
    def validate_security(cls):
        """Validate security configuration and warn about issues"""
        issues = []
        warnings = []
        
        # Check for weak or default values
        if not cls.SECRET_KEY or len(cls.SECRET_KEY) < 32:
            issues.append("SECRET_KEY is too weak or missing")
        
        if cls.DATABASE_URL and 'sqlite' in cls.DATABASE_URL.lower():
            warnings.append("Using SQLite database (not recommended for production)")
        
        if cls.MAIL_PASSWORD == '*** MIGRATED TO DATABASE - ROTATE IMMEDIATELY ***':
            issues.append("🚨 CRITICAL: Default Gmail password is exposed!")
        
        if not cls.SSO_ENCRYPTION_KEY:
            issues.append("SSO_ENCRYPTION_KEY is missing")
        
        # Print results
        if issues:
            print("🚨 SECURITY ISSUES:")
            for issue in issues:
                print(f"  ❌ {issue}")
        
        if warnings:
            print("⚠️ SECURITY WARNINGS:")
            for warning in warnings:
                print(f"  ⚠️ {warning}")
        
        if not issues and not warnings:
            print("✅ Security configuration looks good!")
        
        return len(issues) == 0

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration with enhanced security"""
    DEBUG = False
    TESTING = False
    FLASK_ENV = 'production'
    
    # Enforce HTTPS in production
    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SECURE = True
    
    # Additional security headers
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache
    
    @classmethod
    def validate_production_security(cls):
        """Additional production security validation"""
        issues = []
        
        # Production-specific checks
        if 'sqlite' in cls.SQLALCHEMY_DATABASE_URI.lower():
            issues.append("SQLite not suitable for production")
        
        if not cls.MAIL_USERNAME or not cls.MAIL_PASSWORD:
            issues.append("Email configuration required for production")
        
        if not cls.SSO_ENCRYPTION_KEY:
            issues.append("SSO encryption key required for production")
        
        if issues:
            print("🚨 PRODUCTION SECURITY ISSUES:")
            for issue in issues:
                print(f"  ❌ {issue}")
            return False
        
        print("✅ Production security validation passed!")
        return True

# Auto-detect configuration based on environment
if os.environ.get('FLASK_ENV') == 'production':
    AppConfig = ProductionConfig
else:
    AppConfig = DevelopmentConfig
