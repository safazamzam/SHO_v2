from app import app, db
from models.models import User
from werkzeug.security import generate_password_hash

# Initialize Flask app context
with app.app_context():
    print("=== CREATING TEST USER ===")
    
    # Check if test user already exists
    test_user = User.query.filter_by(username='testuser').first()
    if test_user:
        print("✅ Test user already exists")
        print(f"   Username: {test_user.username}")
        print(f"   Email: {test_user.email}")
    else:
        # Create a simple test user
        test_user = User(
            username='testuser',
            email='test@example.com',
            password=generate_password_hash('password123'),
            role='super_admin',
            first_name='Test',
            last_name='User',
            is_active=True
        )
        
        db.session.add(test_user)
        db.session.commit()
        print("✅ Test user created successfully")
        print("   Username: testuser")
        print("   Password: password123")
        print("   Role: super_admin")
    
    print("\n=== UPDATED USER LIST ===")
    users = User.query.filter(User.role.in_(['super_admin', 'account_admin'])).all()
    for user in users:
        print(f"   {user.username} | {user.email} | {user.role}")
    
    print("\n=== ALTERNATIVE CREDENTIALS TO TRY ===")
    print("1. Username: superadmin | Password: admin123")
    print("2. Username: testuser | Password: password123")
    print("3. Username: techcorp_admin | Password: [try common passwords]")
    print("4. Username: sajid_mohammad@epam.com | Password: [try common passwords]")