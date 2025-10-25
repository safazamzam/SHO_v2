import os
import logging
from cryptography.fernet import Fernet

# Remove .env loading - we'll use Docker secrets + database
# load_dotenv()  # Disabled

class SecureConfigManager:
    """Secure configuration manager for Docker secrets + database storage"""
    
    @staticmethod
    def get_docker_secret(secret_name, default=None, required=False):
        """
        Get secret from Docker secrets (highest priority for critical credentials)
        Falls back to environment variables and then defaults for development
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
        
        # Fallback to environment variables for development
        env_value = os.environ.get(secret_name.upper())
        if env_value:
            logging.info(f"✅ Loaded {secret_name} from environment variable")
            return env_value
        
        # Check if running in development mode
        is_development = os.environ.get('FLASK_ENV', 'development') == 'development'
        
        # For development, provide secure defaults instead of failing
        if is_development and secret_name in ['secret_key', 'secrets_master_key']:
            if secret_name == 'secret_key':
                # Read from secrets file if it exists, otherwise generate
                secret_file_path = './secrets/secret_key.txt'
                if os.path.exists(secret_file_path):
                    try:
                        with open(secret_file_path, 'r') as f:
                            value = f.read().strip()
                            logging.info(f"✅ Loaded {secret_name} from local secrets file")
                            return value
                    except Exception as e:
                        logging.warning(f"Could not read local secret file: {e}")
                
                # Generate secure key for development
                from cryptography.fernet import Fernet
                dev_key = Fernet.generate_key().decode()
                logging.warning(f"⚠️ Generated temporary {secret_name} for development: {dev_key}")
                return dev_key
                
            elif secret_name == 'secrets_master_key':
                # Read from secrets file if it exists, otherwise generate
                secret_file_path = './secrets/secrets_master_key.txt'
                if os.path.exists(secret_file_path):
                    try:
                        with open(secret_file_path, 'r') as f:
                            value = f.read().strip()
                            logging.info(f"✅ Loaded {secret_name} from local secrets file")
                            return value
                    except Exception as e:
                        logging.warning(f"Could not read local secret file: {e}")
                
                # Generate secure master key for development
                from cryptography.fernet import Fernet
                dev_key = Fernet.generate_key().decode()
                logging.warning(f"⚠️ Generated temporary {secret_name} for development: {dev_key}")
                return dev_key
        
        # Return default or raise error
        if required and default is None and not is_development:
            raise ValueError(f"❌ Required secret '{secret_name}' not found in Docker secrets or environment")
        
        if default is not None:
            logging.info(f"✅ Using default value for {secret_name}")
            return default
        
        logging.warning(f"⚠️ Secret {secret_name} not found, returning None")
        return None
    
    @staticmethod
    def build_database_url():
        """Build database URL from Docker secrets or environment variables"""
        # Try to get individual components for Docker secrets
        host = os.environ.get('DATABASE_HOST', 'localhost')
        port = os.environ.get('DATABASE_PORT', '3306')
        name = os.environ.get('DATABASE_NAME', 'shift_handover')
        user = os.environ.get('DATABASE_USER', 'user')
        
        # Get password from Docker secret
        password = SecureConfigManager.get_docker_secret('mysql_user_password')
        
        if password:
            database_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
            logging.info("✅ Built database URL from Docker secrets")
            return database_url
        
        # Fallback to full DATABASE_URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            logging.info("✅ Using DATABASE_URL from environment")
            return database_url
        
        # Development fallback - always use SQLite for development when no database configured
        logging.warning("⚠️ No database credentials found, using SQLite for development")
        return 'sqlite:///shift_handover.db'
        
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
    """Base configuration class with Docker secrets + database storage"""
    
    # Core Flask settings - FROM DOCKER SECRETS OR DEVELOPMENT FALLBACKS
    SECRET_KEY = secure_config.get_docker_secret('secret_key', required=False)
    
    # Database configuration - FROM DOCKER SECRETS OR DEVELOPMENT FALLBACKS  
    SQLALCHEMY_DATABASE_URI = secure_config.build_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Master key for encrypting secrets in database - FROM DOCKER SECRETS OR DEVELOPMENT FALLBACKS
    SECRETS_MASTER_KEY = secure_config.get_docker_secret('secrets_master_key', required=False)
    
    # All other configuration will be loaded from database via SecretsManager
    # This includes:
    # - SMTP settings (server, port, username, password)
    # - ServiceNow configuration
    # - OAuth settings
    # - Application-specific settings
    
    # Default values - will be overridden by database
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = None
    TEAM_EMAIL = None
    
    SERVICENOW_INSTANCE = None
    SERVICENOW_USERNAME = None
    SERVICENOW_PASSWORD = None
    SERVICENOW_TIMEOUT = 30
    SERVICENOW_ASSIGNMENT_GROUPS = ''
    SERVICENOW_ENABLED = False
    
    GOOGLE_OAUTH_CLIENT_ID = None
    GOOGLE_OAUTH_CLIENT_SECRET = None
    
    SESSION_TIMEOUT = 3600
    MAX_WORKERS = 4
    LOG_LEVEL = 'INFO'
    
    # Timezone configuration
    APP_TIMEZONE = 'Asia/Kolkata'
    
    # Shift timing configuration 
    DAY_SHIFT_START = '06:30'
    DAY_SHIFT_END = '15:30'
    EVENING_SHIFT_START = '14:45'
    EVENING_SHIFT_END = '23:45'
    NIGHT_SHIFT_START = '21:45'
    NIGHT_SHIFT_END = '06:45'
    
    @classmethod
    def init_from_database(cls, secrets_manager):
        """Initialize configuration from database-stored secrets"""
        try:
            # Load SMTP configuration from database
            cls.MAIL_SERVER = secrets_manager.get_secret('smtp_server', 'smtp.gmail.com')
            cls.MAIL_PORT = int(secrets_manager.get_secret('smtp_port', 587))
            cls.MAIL_USERNAME = secrets_manager.get_secret('smtp_username')
            cls.MAIL_PASSWORD = secrets_manager.get_secret('smtp_password')
            cls.MAIL_USE_TLS = True
            cls.MAIL_USE_SSL = False
            cls.MAIL_DEFAULT_SENDER = secrets_manager.get_secret('smtp_from', cls.MAIL_USERNAME)
            cls.TEAM_EMAIL = cls.MAIL_DEFAULT_SENDER
            
            # Load ServiceNow configuration from database
            cls.SERVICENOW_INSTANCE = secrets_manager.get_secret('servicenow_instance')
            cls.SERVICENOW_USERNAME = secrets_manager.get_secret('servicenow_username')
            cls.SERVICENOW_PASSWORD = secrets_manager.get_secret('servicenow_password')
            cls.SERVICENOW_TIMEOUT = int(secrets_manager.get_secret('servicenow_timeout', 30))
            cls.SERVICENOW_ASSIGNMENT_GROUPS = secrets_manager.get_secret('servicenow_assignment_groups', '')
            cls.SERVICENOW_ENABLED = secrets_manager.get_secret('servicenow_enabled', 'false').lower() == 'true'
            
            # Load OAuth configuration from database
            cls.GOOGLE_OAUTH_CLIENT_ID = secrets_manager.get_secret('google_oauth_client_id')
            cls.GOOGLE_OAUTH_CLIENT_SECRET = secrets_manager.get_secret('google_oauth_client_secret')
            
            # Load application settings from database
            cls.SESSION_TIMEOUT = int(secrets_manager.get_secret('session_timeout', 3600))
            cls.MAX_WORKERS = int(secrets_manager.get_secret('max_workers', 4))
            cls.LOG_LEVEL = secrets_manager.get_secret('log_level', 'INFO')
            
            # Load timezone configuration
            cls.APP_TIMEZONE = secrets_manager.get_secret('app_timezone', 'Asia/Kolkata')
            
            # Load shift timing configuration
            cls.DAY_SHIFT_START = secrets_manager.get_secret('day_shift_start', '06:30')
            cls.DAY_SHIFT_END = secrets_manager.get_secret('day_shift_end', '15:30')
            cls.EVENING_SHIFT_START = secrets_manager.get_secret('evening_shift_start', '14:45')
            cls.EVENING_SHIFT_END = secrets_manager.get_secret('evening_shift_end', '23:45')
            cls.NIGHT_SHIFT_START = secrets_manager.get_secret('night_shift_start', '21:45')
            cls.NIGHT_SHIFT_END = secrets_manager.get_secret('night_shift_end', '06:45')
            
            logging.info("✅ Configuration loaded from database successfully")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error loading configuration from database: {e}")
            return False
    
    # Security settings
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # HTTPS and Domain Configuration
    APP_DOMAIN = os.environ.get('APP_DOMAIN', 'localhost')
    APP_BASE_URL = os.environ.get('APP_BASE_URL', 'http://localhost:5000')
    FORCE_HTTPS = os.environ.get('FORCE_HTTPS', 'false').lower() == 'true'
    SECURE_HEADERS = os.environ.get('SECURE_HEADERS', 'false').lower() == 'true'
    
    # Trust proxy headers for HTTPS detection
    PREFERRED_URL_SCHEME = 'https' if FORCE_HTTPS else 'http'
    
    @classmethod
    def configure_https_headers(cls, app):
        """Configure HTTPS security headers and settings"""
        if cls.FORCE_HTTPS:
            from flask_talisman import Talisman
            
            # Configure Content Security Policy
            csp = {
                'default-src': ["'self'"],
                'script-src': ["'self'", "'unsafe-inline'", 'cdnjs.cloudflare.com', 'cdn.jsdelivr.net'],
                'style-src': ["'self'", "'unsafe-inline'", 'cdnjs.cloudflare.com', 'fonts.googleapis.com'],
                'font-src': ["'self'", 'fonts.gstatic.com', 'cdnjs.cloudflare.com'],
                'img-src': ["'self'", 'data:', 'https:'],
                'connect-src': ["'self'"],
                'form-action': ["'self'"],
                'frame-ancestors': ["'none'"],
                'object-src': ["'none'"],
                'base-uri': ["'self'"]
            }
            
            # Apply Talisman for security headers
            Talisman(app, 
                force_https=True,
                strict_transport_security=True,
                strict_transport_security_max_age=31536000,
                content_security_policy=csp,
                content_security_policy_nonce_in=['script-src', 'style-src'],
                force_file_save=False
            )
        
        # Configure Flask session security
        app.config['SESSION_COOKIE_SECURE'] = cls.FORCE_HTTPS
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        
        # Add security headers middleware
        @app.after_request
        def add_security_headers(response):
            if cls.SECURE_HEADERS:
                response.headers['X-Content-Type-Options'] = 'nosniff'
                response.headers['X-Frame-Options'] = 'SAMEORIGIN'
                response.headers['X-XSS-Protection'] = '1; mode=block'
                response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
                
                if cls.FORCE_HTTPS:
                    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            return response
    
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
