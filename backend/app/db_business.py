"""
Dynamic Business Database Session Utility — Phase 05

Resolves the active external database connection from the CMS DB Connections table,
builds a SQLAlchemy engine dynamically, and provides a session generator.

Usage in routers / services:
    business_db = get_business_db(cms_db)
    try:
        customers = customer_repository.search(business_db, ...)
    finally:
        business_db.close()

Engine instances are cached by connection ID to avoid reconnecting on every request.
The cache is invalidated when a connection is deactivated or updated.

Oracle support uses python-oracledb (thin mode — no Oracle Instant Client required).
PostgreSQL support uses psycopg2.
"""

import logging
from typing import Dict, Optional

from fastapi import HTTPException, status
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.models import DatabaseConnection, DatabaseConnectionType

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Engine cache
# ---------------------------------------------------------------------------

_engine_cache: Dict[str, Engine] = {}


def invalidate_engine(connection_id: str) -> None:
    """Remove a cached engine — call this when a connection is updated or deactivated."""
    engine = _engine_cache.pop(connection_id, None)
    if engine:
        try:
            engine.dispose()
        except Exception:
            pass


def clear_engine_cache() -> None:
    """Dispose all cached engines (e.g. on shutdown)."""
    for engine in _engine_cache.values():
        try:
            engine.dispose()
        except Exception:
            pass
    _engine_cache.clear()


# ---------------------------------------------------------------------------
# Engine builder
# ---------------------------------------------------------------------------

def _decrypt(encrypted_password: str) -> str:
    from app.services.db_connection_service import decrypt_password
    return decrypt_password(encrypted_password)


def get_business_engine(connection: DatabaseConnection) -> Engine:
    """
    Return a cached SQLAlchemy engine for the given DatabaseConnection.
    Supports Oracle (python-oracledb thin mode) and PostgreSQL (psycopg2).
    """
    if connection.id in _engine_cache:
        return _engine_cache[connection.id]

    plain_password = _decrypt(connection.encrypted_password)

    if connection.database_type == DatabaseConnectionType.ORACLE:
        # python-oracledb thin mode (no Oracle Instant Client required)
        # dialect: oracle+oracledb
        # connect string uses service_name param
        import urllib.parse
        safe_password = urllib.parse.quote_plus(plain_password)
        safe_user = urllib.parse.quote_plus(connection.username)
        url = (
            f"oracle+oracledb://{safe_user}:{safe_password}"
            f"@{connection.host}:{connection.port}/?service_name={connection.service_name}"
        )
        connect_args: dict = {}
    else:
        # postgresql+psycopg2://user:pass@host:port/dbname
        dbname = connection.schema_name or connection.service_name or "postgres"
        url = (
            f"postgresql+psycopg2://{connection.username}:{plain_password}"
            f"@{connection.host}:{connection.port}/{dbname}"
        )
        connect_args = {}

    # Apply schema prefix (e.g. Oracle schema "MAIN") via execution_options so that
    # unqualified table names in models are automatically translated to SCHEMA.table
    schema_name = (connection.schema_name or "").strip() or None
    exec_opts: dict = {}
    if schema_name:
        exec_opts["schema_translate_map"] = {None: schema_name}
        logger.info("Business engine will use schema prefix '%s'", schema_name)

    engine = create_engine(
        url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,
        connect_args=connect_args,
        execution_options=exec_opts or None,
        # Mask credentials in repr/logs
        hide_parameters=True,
    )
    _engine_cache[connection.id] = engine
    logger.info("Business engine created for connection '%s' (type=%s)", connection.connection_name, connection.database_type)
    return engine


# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------

def get_business_db(cms_db: Session) -> Session:
    """
    Resolve the active external DB connection from the CMS database,
    build/retrieve a cached engine, and return a new session.

    When the connection has a schema_name (e.g. Oracle schema "MAIN"), SQLAlchemy's
    schema_translate_map is applied so that unschema'd model tables are automatically
    prefixed — no env var required.

    Raises:
        HTTPException 503 — if no active connection is configured.

    Caller is responsible for closing the returned session.
    """
    from app.repositories.db_connection_repository import db_connection_repository

    connection = db_connection_repository.get_active(cms_db)
    if connection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No active database connection is configured. "
                   "Please activate a connection in Configuration → Database Connections.",
        )

    engine = get_business_engine(connection)
    SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return SessionFactory()
