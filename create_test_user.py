"""
Create a test user for the system
"""

from api.database import get_db
from models.models import User
from api.auth import get_password_hash

def create_test_user():
    """Create a test admin user"""
    db = next(get_db())
    
    # Check if admin user already exists
    existing_user = db.query(User).filter(User.username == "admin").first()
    if existing_user:
        print("✅ Admin user already exists")
        return
    
    # Create admin user
    admin_user = User(
        username="admin",
        email="admin@regisbridge.com",
        first_name="Admin",
        last_name="User",
        password_hash=get_password_hash("admin123"),
        role="ADMIN",
        is_active=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print(f"✅ Created admin user: {admin_user.username}")
    print(f"   Email: {admin_user.email}")
    print(f"   Password: admin123")

if __name__ == "__main__":
    create_test_user()
