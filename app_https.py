# Production Flask app with direct HTTPS support
from flask import Flask, render_template, request
from services.audit_service import log_action
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from config import Config
import os
import ssl

# Import secrets management system
from models.secrets_manager import init_secrets_manager, secrets_manager

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# HTTPS Configuration
def create_ssl_context():
    """Create SSL context for HTTPS"""
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    
    # Use environment variables for certificate paths
    cert_file = os.environ.get('SSL_CERT_PATH', '/app/certs/cert.pem')
    key_file = os.environ.get('SSL_KEY_PATH', '/app/certs/key.pem')
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        context.load_cert_chain(cert_file, key_file)
        return context
    else:
        # Development mode - use adhoc certificates
        return 'adhoc'

# Log every page/tab visit
@app.before_request
def log_page_visit():
    from flask_login import current_user
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        log_action('Page Visit', f'Visited {request.path}')

# Initialize extensions
from models.models import db
from models.servicenow_config import ServiceNowConfig
db.init_app(app)
login_manager = LoginManager(app)
mail = Mail(app)
migrate = Migrate(app, db)

# Import and register blueprints
from routes.main import main_bp
from routes.auth import auth_bp
from routes.handover import handover_bp
from routes.admin import admin_bp
from routes.admin_secrets import admin_secrets_bp
from routes.admin_sso import admin_sso_bp
from routes.admin_servicenow import admin_servicenow_bp
from routes.admin_feature_toggles import admin_feature_toggles_bp
from routes.api import api_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(handover_bp, url_prefix='/handover')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(admin_secrets_bp, url_prefix='/admin')
app.register_blueprint(admin_sso_bp, url_prefix='/admin')
app.register_blueprint(admin_servicenow_bp, url_prefix='/admin')
app.register_blueprint(admin_feature_toggles_bp, url_prefix='/admin')
app.register_blueprint(api_bp, url_prefix='/api')

# Configure Flask-Login
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    from models.models import User
    return User.query.get(int(user_id))

# Patch login/logout to log actions
from flask_login import login_user, logout_user, current_user
import routes.auth
orig_login_user = login_user
orig_logout_user = logout_user

def patched_login_user(user, *args, **kwargs):
    log_action('Login', f'User {getattr(user, "username", user)} logged in')
    return orig_login_user(user, *args, **kwargs)

def patched_logout_user(*args, **kwargs):
    log_action('Logout', f'User {getattr(current_user, "username", current_user)} logged out')
    return orig_logout_user(*args, **kwargs)

# Monkey patch the functions
routes.auth.login_user = patched_login_user
routes.auth.logout_user = patched_logout_user

# Services initialization
def initialize_services():
    """Initialize various services and configurations"""
    try:
        # Initialize secrets manager
        init_secrets_manager(app)
        print("✅ Secrets manager initialized successfully")
        
        # Initialize ServiceNow configuration
        try:
            servicenow_config = ServiceNowConfig.get_config()
            if servicenow_config:
                print("✅ ServiceNow configuration loaded")
            else:
                print("⚠️ ServiceNow configuration not found - creating default")
                ServiceNowConfig.create_default_config()
        except Exception as e:
            print(f"⚠️ ServiceNow configuration error: {e}")
            
    except Exception as e:
        print(f"❌ Service initialization error: {e}")

# Support for both old and new Flask versions
try:
    @app.before_first_request
    def init_services_old():
        initialize_services()
except AttributeError:
    with app.app_context():
        initialize_services()

@app.route('/health')
def health_check():
    """Health check endpoint for load balancers"""
    return {'status': 'healthy', 'service': 'shift-handover'}, 200

@app.route('/smtp-test')
def smtp_test():
    """Test page for SMTP configuration"""
    return render_template('smtp_test.html')

# HTTPS URL schemes
@app.before_request
def force_https():
    """Force HTTPS in production"""
    if os.environ.get('FLASK_ENV') == 'production':
        if not request.is_secure and request.headers.get('X-Forwarded-Proto') != 'https':
            return redirect(request.url.replace('http://', 'https://'))

if __name__ == "__main__":
    # Production HTTPS server
    if os.environ.get('FLASK_ENV') == 'production':
        ssl_context = create_ssl_context()
        app.run(
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)),
            ssl_context=ssl_context,
            debug=False
        )
    else:
        # Development server
        app.run(debug=True)