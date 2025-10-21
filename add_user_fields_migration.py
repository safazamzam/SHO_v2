#!/usr/bin/env python3
"""
Database migration script to add first_name, last_name, and profile_picture fields to User model
"""

from app import app, db
from models.models import User
import sqlalchemy as sa

def migrate_user_table():
    """Add new fields to User table"""
    with app.app_context():
        try:
            # Check if the columns already exist
            inspector = sa.inspect(db.engine)
            columns = inspector.get_columns('user')
            existing_columns = [col['name'] for col in columns]
            
            print(f"Existing columns in user table: {existing_columns}")
            
            # Add columns if they don't exist
            if 'first_name' not in existing_columns:
                print("Adding first_name column...")
                with db.engine.connect() as conn:
                    conn.execute(sa.text('ALTER TABLE user ADD COLUMN first_name VARCHAR(64)'))
                    conn.commit()
                print("✅ Added first_name column")
            else:
                print("ℹ️ first_name column already exists")
                
            if 'last_name' not in existing_columns:
                print("Adding last_name column...")
                with db.engine.connect() as conn:
                    conn.execute(sa.text('ALTER TABLE user ADD COLUMN last_name VARCHAR(64)'))
                    conn.commit()
                print("✅ Added last_name column")
            else:
                print("ℹ️ last_name column already exists")
                
            if 'profile_picture' not in existing_columns:
                print("Adding profile_picture column...")
                with db.engine.connect() as conn:
                    conn.execute(sa.text('ALTER TABLE user ADD COLUMN profile_picture VARCHAR(255)'))
                    conn.commit()
                print("✅ Added profile_picture column")
            else:
                print("ℹ️ profile_picture column already exists")
            
            # Update existing users with parsed names from email
            print("Updating existing users with parsed names...")
            users = User.query.all()
            
            for user in users:
                if not user.first_name and not user.last_name:
                    # Parse name from email
                    name_part = user.email.split('@')[0].replace('_', ' ').replace('.', ' ')
                    name_words = [word.capitalize() for word in name_part.split()]
                    
                    if len(name_words) >= 2:
                        user.first_name = name_words[0]
                        user.last_name = ' '.join(name_words[1:])
                    elif len(name_words) == 1:
                        user.first_name = name_words[0]
                        user.last_name = ''
                    
                    print(f"Updated user {user.email}: {user.first_name} {user.last_name}")
            
            db.session.commit()
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_user_table()