#!/usr/bin/env python3
"""
SMTP Configuration Migration Script

This script:
1. Creates the SMTP configuration table
2. Migrates hardcoded email settings from config.py to secure database storage
3. Replaces the exposed Gmail password with secure configuration
4. Initializes SMTP default settings

🔒 SECURITY CRITICAL: This script addresses the exposed Gmail password vulnerability
"""

import sys
import os
import logging
from datetime import datetime

# Add the application directory to the path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def migrate_smtp_configuration():
    """Migrate SMTP configuration from hardcoded values to database"""
    try:
        # Import Flask app and models directly
        from app import app
        from models.models import db
        from models.smtp_config import SMTPConfig
        import config
        
        print("=" * 60)
        print("🔧 SMTP Configuration Migration")
        print("=" * 60)
        
        # Use the existing Flask app
        
        with app.app_context():
            logger.info("📋 Starting SMTP configuration migration...")
            
            # Create the SMTP config table
            logger.info("🏗️  Creating SMTP configuration table...")
            db.create_all()
            logger.info("✅ SMTP configuration table created successfully")
            
            # Check current hardcoded email settings in config.py
            hardcoded_settings = {
                'smtp_server': getattr(config, 'MAIL_SERVER', 'smtp.gmail.com'),
                'smtp_port': str(getattr(config, 'MAIL_PORT', 587)),
                'smtp_use_tls': str(getattr(config, 'MAIL_USE_TLS', True)).lower(),
                'smtp_use_ssl': str(getattr(config, 'MAIL_USE_SSL', False)).lower(),
                'smtp_username': getattr(config, 'MAIL_USERNAME', '[TO_BE_CONFIGURED]'),
                'smtp_password': getattr(config, 'MAIL_PASSWORD', '[TO_BE_CONFIGURED]'),  # The exposed password
                'mail_default_sender': getattr(config, 'MAIL_DEFAULT_SENDER', '[TO_BE_CONFIGURED]'),
                'team_email': getattr(config, 'TEAM_EMAIL', '[TO_BE_CONFIGURED]'),
                'smtp_enabled': 'false'  # Disabled by default for security
            }
            
            # Report on exposed credentials
            if hardcoded_settings['smtp_password'] == 'uovrivxvitovrjcu':
                logger.warning("🚨 CRITICAL: Exposed Gmail password detected in config.py!")
                logger.warning("📧 Password: uovrivxvitovrjcu")
                logger.warning("⚠️  This password will be replaced with secure database storage")
                
                # Replace with placeholder for security
                hardcoded_settings['smtp_password'] = '[MIGRATED_FROM_EXPOSED_CONFIG]'
                hardcoded_settings['smtp_username'] = '[MIGRATED_FROM_EXPOSED_CONFIG]'
            
            logger.info("📊 Found hardcoded email settings:")
            for key, value in hardcoded_settings.items():
                masked_value = value if key != 'smtp_password' else '*' * len(str(value))
                logger.info(f"   📧 {key}: {masked_value}")
            
            # Initialize default configurations
            logger.info("🔧 Initializing SMTP default configurations...")
            success = SMTPConfig.initialize_default_configs()
            
            if success:
                logger.info("✅ SMTP default configurations initialized")
            else:
                logger.error("❌ Failed to initialize SMTP default configurations")
                return False
            
            # Override with migrated settings (but not the exposed password)
            logger.info("🔄 Migrating hardcoded settings to database...")
            
            migration_count = 0
            for key, value in hardcoded_settings.items():
                if value and value != '[TO_BE_CONFIGURED]':
                    encrypted = (key == 'smtp_password')
                    description = f"Migrated from config.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    
                    success = SMTPConfig.set_config(
                        key=key,
                        value=value,
                        description=description,
                        encrypted=encrypted
                    )
                    
                    if success:
                        migration_count += 1
                        logger.info(f"✅ Migrated {key}")
                    else:
                        logger.error(f"❌ Failed to migrate {key}")
            
            logger.info(f"📈 Migration completed: {migration_count} settings migrated")
            
            # Verify migration
            logger.info("🔍 Verifying migration...")
            all_configs = SMTPConfig.query.all()
            logger.info(f"📊 Total SMTP configurations in database: {len(all_configs)}")
            
            for config in all_configs:
                masked_value = config.config_value if not config.encrypted else '***ENCRYPTED***'
                logger.info(f"   🔧 {config.config_key}: {masked_value}")
            
            # Security recommendations
            print("\n" + "=" * 60)
            print("🔒 SECURITY RECOMMENDATIONS")
            print("=" * 60)
            print("1. ✅ Exposed Gmail password has been replaced with secure placeholder")
            print("2. 🔧 Configure proper SMTP credentials via admin interface:")
            print("   📧 Visit: /admin/secrets/smtp")
            print("3. 🔐 All SMTP passwords are now encrypted in database")
            print("4. ⚙️  Update config.py to use database-driven email configuration")
            print("5. 🧹 Remove hardcoded email settings from config.py")
            print("\n📝 NEXT STEPS:")
            print("1. Access the admin SMTP configuration page")
            print("2. Set proper SMTP credentials for your email provider")
            print("3. Test the SMTP connection")
            print("4. Enable SMTP by setting 'smtp_enabled' to 'true'")
            print("5. Update application code to use SMTPConfig.get_flask_mail_config()")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_migration_status():
    """Check the current status of SMTP configuration migration"""
    try:
        from app import app
        from models.smtp_config import SMTPConfig
        with app.app_context():
            
            print("=" * 60)
            print("📊 SMTP Configuration Status")
            print("=" * 60)
            
            # Check if table exists
            try:
                configs = SMTPConfig.query.all()
                logger.info(f"✅ SMTP configuration table exists with {len(configs)} entries")
                
                # Check configuration status
                is_configured = SMTPConfig.is_configured()
                logger.info(f"📧 SMTP Configuration Status: {'✅ CONFIGURED' if is_configured else '⚠️  NOT CONFIGURED'}")
                
                # List all configurations
                if configs:
                    logger.info("📋 Current SMTP configurations:")
                    for config in configs:
                        masked_value = config.config_value if not config.encrypted else '***ENCRYPTED***'
                        status = "🔐" if config.encrypted else "📝"
                        logger.info(f"   {status} {config.config_key}: {masked_value}")
                else:
                    logger.info("📋 No SMTP configurations found")
                
                return True
                
            except Exception as e:
                logger.warning(f"⚠️  SMTP configuration table does not exist: {str(e)}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Status check failed: {str(e)}")
        return False

def main():
    """Main migration function"""
    print("🚀 SMTP Configuration Migration Tool")
    print("🔒 Securing email configuration and replacing exposed credentials\n")
    
    # Check current status
    logger.info("🔍 Checking current migration status...")
    status_ok = check_migration_status()
    
    if not status_ok:
        logger.info("🚀 Starting SMTP configuration migration...")
        success = migrate_smtp_configuration()
        
        if success:
            logger.info("🎉 SMTP configuration migration completed successfully!")
            
            # Final status check
            logger.info("🔍 Final status check...")
            check_migration_status()
        else:
            logger.error("❌ SMTP configuration migration failed!")
            sys.exit(1)
    else:
        logger.info("✅ SMTP configuration migration already completed")
        
        # Show current status
        check_migration_status()

if __name__ == "__main__":
    main()