import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.server.database import SessionLocal, engine
from backend.server.models import Base, User
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

def create_admin_user():
    """Create admin user"""
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print("✅ Admin user already exists")
            return
        
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@predictions.com",
            hashed_password=pwd_context.hash("admin123"),
            points=10000,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        print("✅ Admin user created")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Points: 10000")
        
    except IntegrityError as e:
        db.rollback()
        print(f"⚠️ Error creating admin: {e}")
    finally:
        db.close()

def create_test_users():
    """Create test users"""
    db = SessionLocal()
    try:
        test_users = [
            {
                "username": "test1",
                "email": "test1@example.com",
                "password": "test123",
                "points": 1500
            },
            {
                "username": "test2", 
                "email": "test2@example.com",
                "password": "test123",
                "points": 2000
            },
            {
                "username": "player1",
                "email": "player1@example.com",
                "password": "player123",
                "points": 800
            }
        ]
        
        for user_data in test_users:
            # Check if user exists
            existing = db.query(User).filter(User.username == user_data["username"]).first()
            if existing:
                print(f"✅ User {user_data['username']} already exists")
                continue
            
            # Create user
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=pwd_context.hash(user_data["password"]),
                points=user_data["points"]
            )
            
            db.add(user)
            print(f"✅ Created user: {user_data['username']} ({user_data['points']} points)")
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"⚠️ Error creating test users: {e}")
    finally:
        db.close()

def main():
    print("🔧 Seeding database...")
    print("-" * 40)
    
    create_tables()
    print()
    create_admin_user()
    print()
    create_test_users()
    print("-" * 40)
    print("✅ Seed data creation complete!")

if __name__ == "__main__":
    main()
