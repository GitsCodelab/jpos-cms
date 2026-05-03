"""
Service layer for Database Connection management.

Handles:
- Credential encryption/decryption
- Business validation
- Connection testing (Oracle and PostgreSQL)
- Active connection management
"""

import os
import time
import logging
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models import DatabaseConnection, DatabaseConnectionType
from app.repositories.db_connection_repository import db_connection_repository
from app.schemas import (
    DatabaseConnectionCreate,
    DatabaseConnectionTestResponse,
    DatabaseConnectionUpdate,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Encryption helpers
# ---------------------------------------------------------------------------

def _get_fernet():
    """Return a Fernet instance using the configured encryption key."""
    try:
        from cryptography.fernet import Fernet
        key = os.getenv("DB_ENCRYPTION_KEY")
        if not key:
            raise RuntimeError("DB_ENCRYPTION_KEY environment variable is not set.")
        # Ensure the key is valid Fernet key (32 url-safe base64 bytes → 44 chars)
        key_bytes = key.encode() if isinstance(key, str) else key
        return Fernet(key_bytes)
    except ImportError:
        raise RuntimeError("cryptography package is not installed. Run: pip install cryptography")


def encrypt_password(plain_password: str) -> str:
    """Encrypt a plain-text password for storage."""
    fernet = _get_fernet()
    return fernet.encrypt(plain_password.encode()).decode()


def decrypt_password(encrypted_password: str) -> str:
    """Decrypt a stored encrypted password."""
    fernet = _get_fernet()
    return fernet.decrypt(encrypted_password.encode()).decode()


# ---------------------------------------------------------------------------
# Service class
# ---------------------------------------------------------------------------

class DatabaseConnectionService:
    """Business logic for database connection management."""

    def create(self, db: Session, data: DatabaseConnectionCreate) -> DatabaseConnection:
        """Create a new database connection with encrypted password."""
        existing = db_connection_repository.get_by_name(db, data.connection_name)
        if existing:
            raise ValueError(f"Connection name '{data.connection_name}' already exists.")

        encrypted = encrypt_password(data.password)
        return db_connection_repository.create(
            db,
            connection_name=data.connection_name,
            database_type=data.database_type,
            host=data.host,
            port=data.port,
            service_name=data.service_name,
            username=data.username,
            encrypted_password=encrypted,
            schema_name=data.schema_name,
            description=data.description,
            is_active=data.is_active,
        )

    def update(self, db: Session, connection_id: str,
               data: DatabaseConnectionUpdate) -> DatabaseConnection:
        """Update an existing connection. Re-encrypts password if provided."""
        connection = db_connection_repository.get_by_id(db, connection_id)
        if not connection:
            raise LookupError(f"Database connection '{connection_id}' not found.")

        fields = data.model_dump(exclude_unset=True)

        # Re-encrypt password if supplied
        if "password" in fields:
            fields["encrypted_password"] = encrypt_password(fields.pop("password"))

        # Check name uniqueness if being renamed
        if "connection_name" in fields and fields["connection_name"] != connection.connection_name:
            existing = db_connection_repository.get_by_name(db, fields["connection_name"])
            if existing:
                raise ValueError(f"Connection name '{fields['connection_name']}' already exists.")

        return db_connection_repository.update(db, connection, **fields)

    def delete(self, db: Session, connection_id: str) -> None:
        """Delete a database connection."""
        connection = db_connection_repository.get_by_id(db, connection_id)
        if not connection:
            raise LookupError(f"Database connection '{connection_id}' not found.")
        db_connection_repository.delete(db, connection)

    def get(self, db: Session, connection_id: str) -> DatabaseConnection:
        """Get a single connection by ID."""
        connection = db_connection_repository.get_by_id(db, connection_id)
        if not connection:
            raise LookupError(f"Database connection '{connection_id}' not found.")
        return connection

    def list(self, db: Session, *, page: int = 1, page_size: int = 20,
             database_type: Optional[DatabaseConnectionType] = None,
             is_active: Optional[bool] = None,
             search: Optional[str] = None) -> Tuple[List[DatabaseConnection], int]:
        """List connections with pagination and optional filters."""
        skip = (page - 1) * page_size
        return db_connection_repository.list(
            db, skip=skip, limit=page_size,
            database_type=database_type,
            is_active=is_active,
            search=search,
        )

    def set_active(self, db: Session, connection_id: str,
                   is_active: bool) -> DatabaseConnection:
        """Activate a connection exclusively (deactivates all others) or deactivate it.

        Only one connection can be active at a time. Activating a connection
        automatically deactivates all other connections.
        """
        connection = db_connection_repository.get_by_id(db, connection_id)
        if not connection:
            raise LookupError(f"Database connection '{connection_id}' not found.")

        if is_active:
            # Deactivate all other connections before activating this one
            db_connection_repository.deactivate_all_except(db, exclude_id=connection_id)

        return db_connection_repository.set_active(db, connection, is_active)

    def get_active_connection(self, db: Session) -> Optional[DatabaseConnection]:
        """Return the currently active connection, or None if none is active.

        Used by business services (reconciliation, fraud, reporting, etc.)
        to obtain the configured external database connection.
        """
        return db_connection_repository.get_active(db)

    def test_connection(self, db: Session,
                        connection_id: str) -> DatabaseConnectionTestResponse:
        """Test live connectivity for a stored connection."""
        connection = db_connection_repository.get_by_id(db, connection_id)
        if not connection:
            raise LookupError(f"Database connection '{connection_id}' not found.")

        try:
            plain_password = decrypt_password(connection.encrypted_password)
        except Exception:
            return DatabaseConnectionTestResponse(
                connection_id=connection_id,
                success=False,
                message="Failed to decrypt stored credentials.",
            )

        if connection.database_type == DatabaseConnectionType.POSTGRESQL:
            return self._test_postgresql(connection_id, connection.host, connection.port,
                                          connection.service_name, connection.username,
                                          plain_password)
        elif connection.database_type == DatabaseConnectionType.ORACLE:
            return self._test_oracle(connection_id, connection.host, connection.port,
                                      connection.service_name, connection.username,
                                      plain_password)
        else:
            return DatabaseConnectionTestResponse(
                connection_id=connection_id,
                success=False,
                message=f"Unsupported database type: {connection.database_type}",
            )

    # ------------------------------------------------------------------
    # Private connection testers
    # ------------------------------------------------------------------

    def _test_postgresql(self, connection_id: str, host: str, port: int,
                          database: str, username: str,
                          password: str) -> DatabaseConnectionTestResponse:
        try:
            import psycopg2  # type: ignore
            start = time.monotonic()
            conn = psycopg2.connect(
                host=host, port=port, dbname=database,
                user=username, password=password,
                connect_timeout=5,
            )
            latency_ms = (time.monotonic() - start) * 1000
            conn.close()
            return DatabaseConnectionTestResponse(
                connection_id=connection_id,
                success=True,
                message="PostgreSQL connection successful.",
                latency_ms=round(latency_ms, 2),
            )
        except Exception as exc:
            logger.warning("PostgreSQL test failed for %s: %s", connection_id, exc)
            return DatabaseConnectionTestResponse(
                connection_id=connection_id,
                success=False,
                message="Connection failed. Check host, port, credentials and database name.",
            )

    def _test_oracle(self, connection_id: str, host: str, port: int,
                     service_name: str, username: str,
                     password: str) -> DatabaseConnectionTestResponse:
        try:
            import oracledb  # type: ignore
            start = time.monotonic()
            dsn = f"{host}:{port}/{service_name}"
            conn = oracledb.connect(user=username, password=password, dsn=dsn)
            latency_ms = (time.monotonic() - start) * 1000
            conn.close()
            return DatabaseConnectionTestResponse(
                connection_id=connection_id,
                success=True,
                message="Oracle connection successful.",
                latency_ms=round(latency_ms, 2),
            )
        except Exception as exc:
            logger.warning("Oracle test failed for %s: %s", connection_id, exc)
            return DatabaseConnectionTestResponse(
                connection_id=connection_id,
                success=False,
                message="Connection failed. Check host, port, credentials and service name.",
            )


db_connection_service = DatabaseConnectionService()
