import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    # Use SQLite for development (easier setup)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///shift_handover.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Flask-Mail config for Gmail SMTP
    MAIL_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('SMTP_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('SMTP_USERNAME', 'mdsajid020@gmail.com')
    MAIL_PASSWORD = os.getenv('SMTP_PASSWORD', 'uovrivxvitovrjcu')
    MAIL_DEFAULT_SENDER = os.getenv('TEAM_EMAIL', 'mdsajid020@gmail.com')
    TEAM_EMAIL = os.getenv('TEAM_EMAIL', 'mdsajid020@gmail.com')
    
    # ServiceNow Integration Configuration
    SERVICENOW_INSTANCE = os.getenv('SERVICENOW_INSTANCE')  # e.g., 'yourcompany.service-now.com'
    SERVICENOW_USERNAME = os.getenv('SERVICENOW_USERNAME')
    SERVICENOW_PASSWORD = os.getenv('SERVICENOW_PASSWORD')
    SERVICENOW_API_VERSION = os.getenv('SERVICENOW_API_VERSION', 'v1')
    SERVICENOW_TIMEOUT = int(os.getenv('SERVICENOW_TIMEOUT', 30))
    SERVICENOW_ENABLED = os.getenv('SERVICENOW_ENABLED', 'false').lower() == 'true'
    SERVICENOW_ASSIGNMENT_GROUPS = os.getenv('SERVICENOW_ASSIGNMENT_GROUPS', '')
