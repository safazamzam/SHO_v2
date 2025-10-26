"""
Initialize local SQLite database with test SSO user
"""
import os
import sys

# Force local SQLite before importing app
os.environ['DATABASE_URL'] = 'sqlite:///shift_handover.db'

from app import app, db
from models.models import User

def init_local_db():
    """Initialize SQLite database with tables and test SSO user"""
    with app.app_context():
        try:
            # Create all tables
            print("🔧 Creating database tables...")
            db.create_all()
            
            # Check if we already have users
            existing_users = User.query.all()
            print(f"📊 Found {len(existing_users)} existing users")
            
            # Create a test SSO user if none exists
            if not existing_users:
                print("👤 Creating test SSO user...")
                test_user = User(
                    username='sso_test_user@example.com',
                    email='sso_test_user@example.com',
                    first_name='John',
                    last_name='Doe',
                    profile_picture='https://i.pravatar.cc/150?img=1',
                    password='',  # Empty password indicates SSO user
                    role='user',
                    is_active=True
                )
                db.session.add(test_user)
                db.session.commit()
                print(f"✅ Created test SSO user: {test_user.username}")
                print(f"   Display Name: {test_user.display_name}")
                print(f"   Profile Picture: {test_user.profile_picture}")
            
            # Create a regular test user for comparison
            regular_user = User.query.filter_by(username='testuser').first()
            if not regular_user:
                print("👤 Creating regular test user...")
                regular_user = User(
                    username='testuser',
                    email='testuser@example.com',
                    first_name='Test',
                    last_name='User',
                    password='testpass',  # Regular password (plain text for now)
                    role='user',
                    is_active=True
                )
                db.session.add(regular_user)
                db.session.commit()
                print(f"✅ Created regular test user: {regular_user.username}")
            
            # Display all users for verification
            all_users = User.query.all()
            print(f"\n📋 Total users in database: {len(all_users)}")
            for user in all_users:
                print(f"   - {user.username} (Role: {user.role})")
                print(f"     Display Name: {user.display_name}")
                print(f"     Profile Picture: {user.profile_picture or 'None'}")
                print(f"     SSO User: {'Yes' if not user.password else 'No'}")
                print()
            
            print("✅ Database initialization complete!")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            return False

if __name__ == '__main__':
    if init_local_db():
        print("🎉 Database ready! You can now test the application.")
        print("📝 Test credentials:")
        print("   Regular User: testuser / testpass")
        print("   SSO User: sso_test_user@example.com (profile should show John Doe with picture)")
    else:
        print("💥 Database initialization failed!")