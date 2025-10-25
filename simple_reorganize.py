#!/usr/bin/env python3
"""Simple script to reorganize secrets for unified dashboard"""

from app import app, db
from sqlalchemy import text

def main():
    with app.app_context():
        print("🔧 REORGANIZING SECRETS FOR UNIFIED DASHBOARD")
        print("=" * 50)
        
        # Update categories to new structure
        updates = [
            # External APIs - SMTP and ServiceNow credentials
            ("external_apis", ["SMTP_USERNAME", "SMTP_PASSWORD", "SERVICENOW_INSTANCE", "SERVICENOW_USERNAME", "SERVICENOW_PASSWORD"]),
            # Application Config - App settings
            ("application_config", ["TEAM_EMAIL", "SERVICENOW_TIMEOUT", "SERVICENOW_API_VERSION", "SERVICENOW_ASSIGNMENT_GROUPS"]),
            # Feature Controls - toggles
            ("feature_controls", ["SERVICENOW_ENABLED"])
        ]
        
        for new_category, secret_keys in updates:
            for key in secret_keys:
                try:
                    query = f"UPDATE secret_store SET category = '{new_category}' WHERE key_name = '{key}'"
                    with db.engine.connect() as connection:
                        result = connection.execute(text(query))
                        connection.commit()
                        if result.rowcount > 0:
                            print(f"✅ {key} → {new_category}")
                except Exception as e:
                    print(f"❌ Error updating {key}: {e}")
        
        # Show final status
        print("\n📊 Final Organization:")
        query = "SELECT category, COUNT(*) as count FROM secret_store GROUP BY category ORDER BY category"
        with db.engine.connect() as connection:
            result = connection.execute(text(query))
            for category, count in result.fetchall():
                print(f"- {category}: {count} secrets")

if __name__ == "__main__":
    main()