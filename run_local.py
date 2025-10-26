"""
Local development configuration override
Forces the app to use SQLite database for local testing
"""
import os

# Force local SQLite database for development
os.environ['DATABASE_HOST'] = 'localhost'
os.environ['DATABASE_URL'] = 'sqlite:///shift_handover.db'

print("🔧 DEVELOPMENT MODE: Forcing SQLite database usage")
print("📁 Database: shift_handover.db")

# Import the main app
from app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)