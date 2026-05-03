"""
Customer Router — Phase 05

Exposes read-only customer management endpoints.
All data is read from the external business database via db_business.get_business_db().

Endpoints:
  GET /customers                  — search with pagination
  GET /customers/{id}             — customer detail
  GET /customers/{id}/contracts   — contract list
  GET /customers/{id}/cards       — card list (masked PAN)
  GET /customers/{id}/accounts    — account list (balance hidden for viewer)
  GET /customers/{id}/documents   — KYC document list
  GET /customers/{id}/contacts    — contact list

Access:
  All endpoints require a valid JWT.
  /accounts balance field is hidden for role=viewer (returns null).
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.security import require_jwt_token
from app.schemas import (
    CustomerSearchResponse,
    CustomerDetailResponse,
    CustomerContractResponse,
    CustomerCardResponse,
    CustomerAccountResponse,
    CustomerDocumentResponse,
    CustomerContactResponse,
)
import app.services.customer_service as customer_service

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=CustomerSearchResponse)
def search_customers(
    q: Optional[str] = Query(None, description="Name / mobile / email / national ID prefix (min 3 chars)"),
    national_id: Optional[str] = Query(None, description="Exact national ID lookup"),
    status: Optional[str] = Query(None, description="Filter by customer status"),
    segment: Optional[str] = Query(None, description="Filter by segment"),
    page: int = Query(1, ge=1, le=200),
    page_size: int = Query(100, ge=1, le=500),
    cms_db: Session = Depends(get_db),
    token: Dict[str, Any] = Depends(require_jwt_token),
) -> CustomerSearchResponse:
    return customer_service.search_customers(
        cms_db,
        q=q,
        national_id=national_id,
        status=status,
        segment=segment,
        page=page,
        page_size=page_size,
    )


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
def get_customer(
    customer_id: str,
    cms_db: Session = Depends(get_db),
    token: Dict[str, Any] = Depends(require_jwt_token),
) -> CustomerDetailResponse:
    return customer_service.get_customer_detail(cms_db, customer_id)


@router.get("/{customer_id}/contracts", response_model=List[CustomerContractResponse])
def get_contracts(
    customer_id: str,
    cms_db: Session = Depends(get_db),
    token: Dict[str, Any] = Depends(require_jwt_token),
) -> List[CustomerContractResponse]:
    return customer_service.get_customer_contracts(cms_db, customer_id)


@router.get("/{customer_id}/cards", response_model=List[CustomerCardResponse])
def get_cards(
    customer_id: str,
    include_pan: bool = Query(False, description="Return full PAN — admin/operator only"),
    cms_db: Session = Depends(get_db),
    token: Dict[str, Any] = Depends(require_jwt_token),
) -> List[CustomerCardResponse]:
    role: str = token.get("role", "viewer")
    # Only admin and operator may request clear PAN
    reveal = include_pan and role in ("admin", "operator")
    return customer_service.get_customer_cards(cms_db, customer_id, include_pan=reveal)


@router.get("/{customer_id}/accounts", response_model=List[CustomerAccountResponse])
def get_accounts(
    customer_id: str,
    cms_db: Session = Depends(get_db),
    token: Dict[str, Any] = Depends(require_jwt_token),
) -> List[CustomerAccountResponse]:
    role: str = token.get("role", "viewer")
    include_balance = role in ("admin", "operator")
    return customer_service.get_customer_accounts(
        cms_db, customer_id, include_balance=include_balance
    )


@router.get("/{customer_id}/documents", response_model=List[CustomerDocumentResponse])
def get_documents(
    customer_id: str,
    cms_db: Session = Depends(get_db),
    token: Dict[str, Any] = Depends(require_jwt_token),
) -> List[CustomerDocumentResponse]:
    return customer_service.get_customer_documents(cms_db, customer_id)


@router.get("/{customer_id}/contacts", response_model=List[CustomerContactResponse])
def get_contacts(
    customer_id: str,
    cms_db: Session = Depends(get_db),
    token: Dict[str, Any] = Depends(require_jwt_token),
) -> List[CustomerContactResponse]:
    return customer_service.get_customer_contacts(cms_db, customer_id)
