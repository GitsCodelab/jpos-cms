#!/usr/bin/env python3
"""Migration runner - executes database migrations without alembic CLI"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db import engine
from app.models import Base, User, UserSession, LoginAudit, TokenBlacklist


def init_db():
    """Initialize database tables using SQLAlchemy."""
    print("🔄 Initializing database schema...")
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database schema initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False


def check_migration_status():
    """Check if migration tables exist."""
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    auth_tables = ['users', 'user_sessions', 'login_audit', 'token_blacklist']
    missing = [t for t in auth_tables if t not in tables]
    
    if missing:
        print(f"⚠️  Missing tables: {', '.join(missing)}")
        return False
    else:
        print("✅ All authentication tables exist")
        return True


def seed_admin_user():
    """Create default admin user if it doesn't exist."""
    from sqlalchemy.orm import sessionmaker
    from app.security import hash_password
    import uuid
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Check if admin exists
        admin = session.query(User).filter(User.username == "admin").first()
        if admin:
            print("✅ Admin user already exists")
            return True
        
        # Create admin user
        admin_user = User(
            id=str(uuid.uuid4()),
            username="admin",
            password_hash=hash_password("admin123"),
            email="admin@jpos-cms.local",
            role="admin",
            is_active=True,
            created_at=datetime.utcnow()
        )
        session.add(admin_user)
        session.commit()
        print(f"✅ Admin user created (ID: {admin_user.id})")
        return True
    except Exception as e:
        session.rollback()
        print(f"⚠️  Could not create admin user: {e}")
        return False
    finally:
        session.close()


def main():
    """Run database migrations."""
    print("\n" + "="*60)
    print("🗄️  Database Migration Runner")
    print("="*60)
    
    # Step 1: Initialize tables
    if not init_db():
        sys.exit(1)
    
    # Step 2: Check status
    if not check_migration_status():
        print("❌ Migration validation failed")
        sys.exit(1)
    
    # Step 3: Seed admin user
    try:
        seed_admin_user()
    except ImportError:
        print("⚠️  Cannot seed admin - hash_password not available")
    
    print("\n" + "="*60)
    print("✅ Database migration completed successfully")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
