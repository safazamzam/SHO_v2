#!/bin/bash

# Database initialization and Flask startup script

echo "🔧 Initializing database..."

# Create database tables using Python
python3 << EOF
try:
    from app import app, db
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")
except Exception as e:
    print(f"⚠️ Database initialization warning: {e}")
    print("🔄 Continuing with Flask startup...")
EOF

# Start Flask application
echo "🚀 Starting Flask application..."
exec flask run