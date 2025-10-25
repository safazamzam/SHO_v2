"""
App integration patch for hybrid secrets management
Add this to your app.py after the existing imports and before app initialization
"""

# Add this import section after your existing imports
from models.secrets_manager import init_secrets_manager, secrets_manager
from routes.admin_secrets import admin_secrets_bp

# Add this function to integrate secrets management
def initialize_secrets_management():
    """Initialize the hybrid secrets management system"""
    try:
        # Import here to avoid circular imports
        from models.models import db
        
        # Initialize secrets manager with database session
        master_key = os.environ.get('SECRETS_MASTER_KEY')
        if not master_key:
            print("⚠️ WARNING: SECRETS_MASTER_KEY not set. Generating temporary key.")
            from cryptography.fernet import Fernet
            master_key = Fernet.generate_key().decode()
            print(f"🔑 Temporary SECRETS_MASTER_KEY: {master_key}")
            print("💡 Set this as environment variable for persistence!")
        
        # Initialize with database session
        init_secrets_manager(db.session, master_key)
        
        print("✅ Hybrid secrets management initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing secrets management: {e}")
        return False

# Add this after your existing app configuration
def configure_app_with_secrets():
    """Configure app using hybrid secrets for dynamic configuration"""
    try:
        # Update app config with secrets from database
        if secrets_manager:
            # Example: Update mail configuration from secrets
            smtp_username = secrets_manager.get_secret('SMTP_USERNAME')
            if smtp_username:
                app.config['MAIL_USERNAME'] = smtp_username
            
            smtp_password = secrets_manager.get_secret('SMTP_PASSWORD')
            if smtp_password:
                app.config['MAIL_PASSWORD'] = smtp_password
            
            # ServiceNow configuration from secrets
            servicenow_instance = secrets_manager.get_secret('SERVICENOW_INSTANCE')
            if servicenow_instance:
                app.config['SERVICENOW_INSTANCE'] = servicenow_instance
            
            servicenow_username = secrets_manager.get_secret('SERVICENOW_USERNAME')
            if servicenow_username:
                app.config['SERVICENOW_USERNAME'] = servicenow_username
            
            servicenow_password = secrets_manager.get_secret('SERVICENOW_PASSWORD')
            if servicenow_password:
                app.config['SERVICENOW_PASSWORD'] = servicenow_password
            
            # Application configuration from secrets
            team_email = secrets_manager.get_secret('TEAM_EMAIL')
            if team_email:
                app.config['TEAM_EMAIL'] = team_email
            
            print("✅ App configuration updated with secrets from database")
            
    except Exception as e:
        print(f"⚠️ Warning: Could not update app config with secrets: {e}")

# Add blueprint registration (add this with your other blueprint registrations)
def register_secrets_blueprint():
    """Register the admin secrets management blueprint"""
    try:
        app.register_blueprint(admin_secrets_bp)
        print("✅ Secrets management admin panel registered at /admin/secrets")
    except Exception as e:
        print(f"❌ Error registering secrets blueprint: {e}")

# Add this to check if user is superadmin (modify based on your user model)
def init_superadmin_check():
    """Initialize superadmin checking for secrets management"""
    from models.models import User  # Adjust based on your user model
    
    # Add superadmin field to user model if not exists
    # This is a simple check - you should implement proper role-based access
    @login_manager.user_loader
    def load_user_with_admin_check(user_id):
        user = User.query.get(int(user_id))
        if user:
            # Simple superadmin check - modify based on your requirements
            # Option 1: Check email domain
            if hasattr(user, 'email') and user.email.endswith('@epam.com'):
                user.is_superadmin = True
            # Option 2: Check specific emails
            elif hasattr(user, 'email') and user.email in ['mdsajid020@gmail.com', 'admin@yourcompany.com']:
                user.is_superadmin = True
            # Option 3: Check user role
            elif hasattr(user, 'role') and user.role == 'superadmin':
                user.is_superadmin = True
            else:
                user.is_superadmin = False
        return user

# Integration steps to add to your app.py:
"""
1. Add the imports at the top of your app.py:
   from models.secrets_manager import init_secrets_manager, secrets_manager
   from routes.admin_secrets import admin_secrets_bp

2. After your app and db initialization, add:
   # Initialize secrets management
   with app.app_context():
       initialize_secrets_management()
       configure_app_with_secrets()

3. Add blueprint registration with your other blueprints:
   register_secrets_blueprint()

4. Modify your user loader or add superadmin checking:
   init_superadmin_check()
"""

print("""
🔐 Secrets Management Integration Guide
=====================================

To integrate hybrid secrets management into your app:

1. Add imports to app.py:
   from models.secrets_manager import init_secrets_manager, secrets_manager
   from routes.admin_secrets import admin_secrets_bp

2. Initialize after app creation:
   with app.app_context():
       initialize_secrets_management()
       configure_app_with_secrets()

3. Register blueprint:
   app.register_blueprint(admin_secrets_bp)

4. Run database migration:
   python migrations/create_secrets_tables.py

5. Set environment variable:
   export SECRETS_MASTER_KEY="your-generated-key"

6. Access admin panel:
   http://localhost:5000/admin/secrets

Security Features:
✅ Critical secrets (DB, keys) stay in environment only
✅ API secrets stored encrypted in database with UI management
✅ Comprehensive audit logging for all secret access
✅ Superadmin-only access with role checking
✅ Automatic encryption/decryption with master key
✅ Secret expiration and rotation support
""")