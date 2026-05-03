"""
Repository for DatabaseConnection CRUD operations.

Handles all database access for the database connections module.
Business logic stays in the service layer.
"""

import uuid
from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import DatabaseConnection, DatabaseConnectionType


class DatabaseConnectionRepository:
    """CRUD repository for DatabaseConnection entities."""

    def create(self, db: Session, *, connection_name: str, database_type: DatabaseConnectionType,
               host: str, port: int, service_name: str, username: str, encrypted_password: str,
               schema_name: Optional[str] = None, description: Optional[str] = None,
               is_active: bool = True) -> DatabaseConnection:
        obj = DatabaseConnection(
            id=str(uuid.uuid4()),
            connection_name=connection_name,
            database_type=database_type,
            host=host,
            port=port,
            service_name=service_name,
            username=username,
            encrypted_password=encrypted_password,
            schema_name=schema_name,
            description=description,
            is_active=is_active,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get_by_id(self, db: Session, connection_id: str) -> Optional[DatabaseConnection]:
        return db.query(DatabaseConnection).filter(DatabaseConnection.id == connection_id).first()

    def get_by_name(self, db: Session, connection_name: str) -> Optional[DatabaseConnection]:
        return db.query(DatabaseConnection).filter(
            DatabaseConnection.connection_name == connection_name
        ).first()

    def list(self, db: Session, *, skip: int = 0, limit: int = 20,
             database_type: Optional[DatabaseConnectionType] = None,
             is_active: Optional[bool] = None,
             search: Optional[str] = None) -> Tuple[List[DatabaseConnection], int]:
        query = db.query(DatabaseConnection)

        if database_type is not None:
            query = query.filter(DatabaseConnection.database_type == database_type)
        if is_active is not None:
            query = query.filter(DatabaseConnection.is_active == is_active)
        if search:
            pattern = f"%{search}%"
            query = query.filter(
                DatabaseConnection.connection_name.ilike(pattern) |
                DatabaseConnection.host.ilike(pattern) |
                DatabaseConnection.description.ilike(pattern)
            )

        total = query.with_entities(func.count(DatabaseConnection.id)).scalar()
        items = query.order_by(DatabaseConnection.connection_name).offset(skip).limit(limit).all()
        return items, total

    def update(self, db: Session, connection: DatabaseConnection, **fields) -> DatabaseConnection:
        for key, value in fields.items():
            if value is not None and hasattr(connection, key):
                setattr(connection, key, value)
        db.commit()
        db.refresh(connection)
        return connection

    def delete(self, db: Session, connection: DatabaseConnection) -> None:
        db.delete(connection)
        db.commit()

    def deactivate_all_except(self, db: Session, exclude_id: str) -> None:
        """Set is_active=False for all connections except the given ID."""
        db.query(DatabaseConnection).filter(
            DatabaseConnection.id != exclude_id
        ).update({"is_active": False}, synchronize_session="fetch")
        db.commit()

    def get_active(self, db: Session) -> Optional[DatabaseConnection]:
        """Return the single active connection, or None."""
        return db.query(DatabaseConnection).filter(
            DatabaseConnection.is_active == True  # noqa: E712
        ).first()

    def set_active(self, db: Session, connection: DatabaseConnection,
                   is_active: bool) -> DatabaseConnection:
        connection.is_active = is_active
        db.commit()
        db.refresh(connection)
        return connection


db_connection_repository = DatabaseConnectionRepository()
