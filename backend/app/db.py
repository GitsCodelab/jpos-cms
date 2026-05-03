"""
SQLAlchemy database configuration and session management.

Supports both PostgreSQL and Oracle databases via environment configuration.
Use BASE for ORM model definitions.
Use get_db() as FastAPI dependency for request-scoped sessions.
"""

import os
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost/jpos_cms"
)

# Additional Oracle parameters (if using Oracle)
ORACLE_MODE = DATABASE_URL.startswith("oracle")

# Engine configuration
if ORACLE_MODE:
    # Oracle-specific settings
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM Base class for model definitions
Base = declarative_base()


def get_db() -> Generator:
    """
    FastAPI dependency: provides request-scoped database session.
    
    Usage in routes:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database: create all tables and seed default admin user."""
    Base.metadata.create_all(bind=engine)
    _seed_admin()


def _seed_admin():
    """Create default admin user if it does not exist."""
    import uuid
    from app.models import User  # local import to avoid circular dependency
    from app.security import hash_password

    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            admin = User(
                id=str(uuid.uuid4()),
                username="admin",
                password_hash=hash_password(os.getenv("AUTH_PASSWORD", "admin123")),
                email="admin@jpos-cms.local",
                role="admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def close_db():
    """Close database connection pool."""
    engine.dispose()


# Event listeners for connection debugging
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Oracle-specific: set connection session parameters."""
    if ORACLE_MODE:
        cursor = dbapi_conn.cursor()
        cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT='YYYY-MM-DD HH24:MI:SS'")
        cursor.close()

