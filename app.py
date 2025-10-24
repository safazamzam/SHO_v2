from flask import Flask, render_template

from services.audit_service import log_action

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from config import Config
import os

# Import secrets management system
from models.secrets_manager import init_secrets_manager, secrets_manager

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Log every page/tab visit
@app.before_request
def log_page_visit():
    from flask_login import current_user
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        log_action('Page Visit', f'Visited {request.path}')


# Initialize extensions
from models.models import db
from models.servicenow_config import ServiceNowConfig  # Import ServiceNow config model
db.init_app(app)
login_manager = LoginManager(app)
mail = Mail(app)
migrate = Migrate(app, db)

# Import blueprints

from routes.auth import auth_bp

# Patch login/logout to log actions
from flask import request
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
routes.auth.login_user = patched_login_user
routes.auth.logout_user = patched_logout_user
from routes.handover import handover_bp
from routes.dashboard import dashboard_bp
from routes.roster import roster_bp

from routes.team import team_bp
from routes.roster_upload import roster_upload_bp
from routes.reports import reports_bp



# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(handover_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(roster_bp)
app.register_blueprint(team_bp)
app.register_blueprint(roster_upload_bp)
app.register_blueprint(reports_bp)
from routes.admin import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

from routes.escalation_matrix import escalation_bp
app.register_blueprint(escalation_bp)

# Register user management blueprint
from routes.user_management import user_mgmt_bp
app.register_blueprint(user_mgmt_bp)

# Register keypoints updates blueprint
from routes.keypoints import keypoints_bp
app.register_blueprint(keypoints_bp)

# Register ctask assignment blueprint
from routes.ctask_assignment import ctask_assignment_bp
app.register_blueprint(ctask_assignment_bp)

# Register config blueprint for admin configuration
from routes.config import config_bp
app.register_blueprint(config_bp)

# Register misc blueprint for 'coming soon' tabs
from routes.misc import misc_bp
app.register_blueprint(misc_bp)

# Register audit logs blueprint
from routes.logs import logs_bp
app.register_blueprint(logs_bp)

# Register SSO authentication blueprints
from routes.sso_auth import sso_auth
from routes.sso_config import sso_config_bp
app.register_blueprint(sso_auth)
app.register_blueprint(sso_config_bp)

# Register user profile blueprint
from routes.user_profile import user_profile_bp
app.register_blueprint(user_profile_bp)

# Register secrets management admin blueprint
from routes.admin_secrets import admin_secrets_bp
app.register_blueprint(admin_secrets_bp)

# Add template global functions
@app.template_global()
def is_tab_enabled(tab_name):
    """Check if a specific tab is enabled based on database configuration."""
    try:
        from models.app_config import AppConfig
        # Get the configuration value from database
        config_value = AppConfig.get_config(tab_name, default='true')
        return config_value.lower() == 'true'
    except Exception as e:
        # Fallback to default values if database not available
        enabled_tabs = {
            'tab_kb_articles': True,
            'tab_vendor_details': True,
            'tab_applications': True,
            'tab_change_management': True,
            'tab_problem_tickets': True,
            'tab_post_mortems': True
        }
        return enabled_tabs.get(tab_name, True)

@app.template_filter('safe_engineer_name')
def safe_engineer_name(engineer):
    """Safely get engineer name from object or dict"""
    try:
        if hasattr(engineer, 'name'):
            return engineer.name
        elif isinstance(engineer, dict) and 'name' in engineer:
            return engineer['name']
        else:
            return str(engineer)
    except:
        return 'Unknown Engineer'

@app.template_global()
def is_feature_enabled(feature_name):
    """Check if a specific feature is enabled based on database configuration."""
    try:
        from models.app_config import AppConfig
        # Get the configuration value from database
        config_value = AppConfig.get_config(feature_name, default='true')
        return config_value.lower() == 'true'
    except Exception as e:
        # Fallback to default values if database not available
        enabled_features = {
            'feature_servicenow_integration': True,
            'feature_ctask_assignment': True
        }
        return enabled_features.get(feature_name, True)

@app.template_global()
def is_servicenow_enabled_and_configured():
    """Check if ServiceNow is both enabled and properly configured"""
    try:
        from models.app_config import AppConfig
        from models.servicenow_config import ServiceNowConfig
        
        # Check feature toggle
        feature_enabled = AppConfig.is_enabled('feature_servicenow_integration')
        
        # Check configuration completeness
        config_complete = ServiceNowConfig.is_configured()
        
        return feature_enabled and config_complete
    except Exception as e:
        return False

@app.template_global()
def is_nav_active(path):
    """Check if the current request path matches the navigation link"""
    from flask import request
    current_path = request.path
    
    # Exact match for root paths
    if path == '/' and current_path == '/':
        return True
    
    # Special case: /reports should be active for /handover-reports since /reports redirects there
    if path == '/reports' and current_path.startswith('/handover-reports'):
        return True
    
    # Special case: /handover should NOT match /handover-reports (to avoid conflict with reports)
    if path == '/handover' and current_path.startswith('/handover-reports'):
        return False
    
    # Special case: /roster should NOT match /roster-upload (to avoid both being highlighted)
    if path == '/roster' and current_path.startswith('/roster-upload'):
        return False
    
    # For other paths, check if current path starts with the nav path
    # Add trailing slash check to ensure exact path matching
    if path != '/':
        # Exact match first
        if current_path == path:
            return True
        # Then check if current path starts with nav path followed by '/' or query params
        if current_path.startswith(path + '/') or current_path.startswith(path + '?'):
            return True
        
    return False

# Add template filters
@app.template_filter('date_day_name')
def date_day_name_filter(date):
    """Convert date to day name (e.g., Monday, Tuesday)"""
    from datetime import datetime
    if isinstance(date, str):
        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return "Unknown"
    elif isinstance(date, datetime):
        date = date.date()
    
    if date:
        return date.strftime('%A')
    return "Unknown"

@app.template_filter('strptime')
def strptime_filter(date_string, format='%Y-%m-%d'):
    """Parse date string to datetime object"""
    from datetime import datetime
    try:
        return datetime.strptime(date_string, format)
    except (ValueError, TypeError):
        return None

@login_manager.user_loader
def load_user(user_id):
    from models.models import User
    return User.query.get(int(user_id))

# Auto-start CTask assignment service when Flask app starts
_services_initialized = False  # Flag to prevent duplicate initialization

def initialize_services():
    """Initialize background services when the Flask app starts"""
    global _services_initialized
    
    # Prevent duplicate initialization
    if _services_initialized:
        return
        
    try:
        # Initialize database configurations
        with app.app_context():
            try:
                # Initialize secrets management system
                from models.models import db
                master_key = os.environ.get('SECRETS_MASTER_KEY')
                if master_key:
                    init_secrets_manager(db.session, master_key)
                    print("✅ Secrets management system initialized successfully")
                    
                    # Store in app context for admin routes access
                    app.secrets_manager = secrets_manager
                    
                    # Update app config with secrets from database
                    if secrets_manager:
                        # Update mail configuration from secrets
                        smtp_username = secrets_manager.get_secret('SMTP_USERNAME')
                        if smtp_username and smtp_username != '[TO_BE_SET_VIA_UI]':
                            app.config['MAIL_USERNAME'] = smtp_username
                            print(f"✅ Updated MAIL_USERNAME from secrets")
                        
                        smtp_password = secrets_manager.get_secret('SMTP_PASSWORD')
                        if smtp_password and smtp_password != '[TO_BE_SET_VIA_UI]':
                            app.config['MAIL_PASSWORD'] = smtp_password
                            print(f"✅ Updated MAIL_PASSWORD from secrets")
                        
                        # ServiceNow configuration from secrets
                        servicenow_instance = secrets_manager.get_secret('SERVICENOW_INSTANCE')
                        if servicenow_instance and servicenow_instance != '[TO_BE_SET_VIA_UI]':
                            app.config['SERVICENOW_INSTANCE'] = servicenow_instance
                            print(f"✅ Updated SERVICENOW_INSTANCE from secrets")
                        
                        servicenow_username = secrets_manager.get_secret('SERVICENOW_USERNAME')
                        if servicenow_username and servicenow_username != '[TO_BE_SET_VIA_UI]':
                            app.config['SERVICENOW_USERNAME'] = servicenow_username
                            print(f"✅ Updated SERVICENOW_USERNAME from secrets")
                        
                        servicenow_password = secrets_manager.get_secret('SERVICENOW_PASSWORD')
                        if servicenow_password and servicenow_password != '[TO_BE_SET_VIA_UI]':
                            app.config['SERVICENOW_PASSWORD'] = servicenow_password
                            print(f"✅ Updated SERVICENOW_PASSWORD from secrets")
                else:
                    print("⚠️ SECRETS_MASTER_KEY not set - secrets management not initialized")
                
                from models.app_config import AppConfig
                from models.servicenow_config import ServiceNowConfig
                
                # Initialize default configurations
                AppConfig.initialize_defaults()
                ServiceNowConfig.initialize_defaults()
                
                print("✅ Configuration defaults initialized")
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize configurations: {e}")
        
        # Check if CTask assignment feature is enabled
        from models.app_config import AppConfig
        if AppConfig.is_enabled('feature_ctask_assignment'):
            # Start the CTask assignment scheduler automatically
            from services.ctask_scheduler import start_ctask_scheduler, get_scheduler_status
            
            # Check if scheduler is already running
            status = get_scheduler_status()
            if not status['running']:
                print("🚀 Auto-starting CTask assignment scheduler...")
                start_ctask_scheduler()
                
                # Configure ServiceNow connection using new configuration system
                try:
                    from services.servicenow_service import ServiceNowService
                    service = ServiceNowService()
                    
                    # Initialize the service with app context so it can use secrets manager fallback
                    service.initialize(app)
                    
                    if service.instance_url and service.username and service.password:
                        print("✅ CTask assignment service started with ServiceNow connection")
                    else:
                        print("⚠️ CTask assignment service started but ServiceNow not configured")
                        
                except Exception as e:
                    print(f"⚠️ CTask assignment service started but ServiceNow configuration failed: {e}")
            else:
                print("✅ CTask assignment scheduler already running")
                
        _services_initialized = True  # Mark as initialized
                
    except Exception as e:
        print(f"❌ Failed to auto-start CTask assignment service: {e}")
        _services_initialized = True  # Mark as attempted even if failed

# Support for both old and new Flask versions
try:
    # For older Flask versions
    @app.before_first_request
    def init_services_old():
        initialize_services()
except AttributeError:
    # For newer Flask versions, we'll call it during app startup
    with app.app_context():
        initialize_services()

# Test route for SMTP configuration
@app.route('/smtp-test')
def smtp_test():
    """Test page for SMTP configuration"""
    return render_template('smtp_test.html')

if __name__ == "__main__":
    app.run(debug=True)
