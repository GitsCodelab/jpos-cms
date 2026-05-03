"""
Configuration router — Database Connections management.
"""

import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import DatabaseConnectionType
from app.schemas import (
    DatabaseConnectionCreate,
    DatabaseConnectionResponse,
    DatabaseConnectionTestResponse,
    DatabaseConnectionUpdate,
    PaginatedDatabaseConnections,
)
from app.security import require_jwt_token
from app.services.db_connection_service import db_connection_service

router = APIRouter(prefix="/config", tags=["config"])


# ---------------------------------------------------------------------------
# Database Connections endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/database-connections",
    response_model=PaginatedDatabaseConnections,
    summary="List database connections",
)
def list_database_connections(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    database_type: Optional[DatabaseConnectionType] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None, max_length=200),
    db: Session = Depends(get_db),
    _: dict = Depends(require_jwt_token),
):
    items, total = db_connection_service.list(
        db, page=page, page_size=page_size,
        database_type=database_type,
        is_active=is_active,
        search=search,
    )
    return PaginatedDatabaseConnections(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get(
    "/database-connections/{connection_id}",
    response_model=DatabaseConnectionResponse,
    summary="Get a single database connection",
)
def get_database_connection(
    connection_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_jwt_token),
):
    try:
        return db_connection_service.get(db, connection_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post(
    "/database-connections",
    response_model=DatabaseConnectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new database connection",
)
def create_database_connection(
    data: DatabaseConnectionCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_jwt_token),
):
    try:
        return db_connection_service.create(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.put(
    "/database-connections/{connection_id}",
    response_model=DatabaseConnectionResponse,
    summary="Update a database connection",
)
def update_database_connection(
    connection_id: str,
    data: DatabaseConnectionUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_jwt_token),
):
    try:
        return db_connection_service.update(db, connection_id, data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.delete(
    "/database-connections/{connection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a database connection",
)
def delete_database_connection(
    connection_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_jwt_token),
):
    try:
        db_connection_service.delete(db, connection_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post(
    "/database-connections/{connection_id}/test",
    response_model=DatabaseConnectionTestResponse,
    summary="Test a database connection",
)
def test_database_connection(
    connection_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_jwt_token),
):
    try:
        return db_connection_service.test_connection(db, connection_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post(
    "/database-connections/{connection_id}/activate",
    response_model=DatabaseConnectionResponse,
    summary="Activate a connection exclusively (deactivates all others)",
)
def activate_database_connection(
    connection_id: str,
    is_active: bool = Query(..., description="Set active state"),
    db: Session = Depends(get_db),
    _: dict = Depends(require_jwt_token),
):
    try:
        return db_connection_service.set_active(db, connection_id, is_active)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get(
    "/database-connections/active",
    response_model=Optional[DatabaseConnectionResponse],
    summary="Get the currently active database connection",
)
def get_active_database_connection(
    db: Session = Depends(get_db),
    _: dict = Depends(require_jwt_token),
):
    return db_connection_service.get_active_connection(db)

