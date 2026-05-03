"""
Customer Service — Phase 05

Orchestrates DB session resolution, repository calls, and data transformation.
All business logic (masking, access control, search validation) lives here.
Routers delegate entirely to this service.
"""

import math
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.db_business import get_business_db
from app.models_business import Customer
from app.repositories.customer_repository import customer_repository
from app.repositories.customer_contract_repository import customer_contract_repository
from app.repositories.customer_card_repository import customer_card_repository
from app.repositories.customer_account_repository import customer_account_repository
from app.repositories.customer_document_repository import customer_document_repository
from app.repositories.customer_contact_repository import customer_contact_repository
from app.schemas import (
    CustomerSearchResult,
    CustomerSearchResponse,
    CustomerDetailResponse,
    CustomerContractResponse,
    CustomerCardResponse,
    CustomerAccountResponse,
    CustomerDocumentResponse,
    CustomerContactResponse,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mask_card(pan: Optional[str]) -> Optional[str]:
    """Return last-4-digit masked PAN: ****-****-****-1234."""
    if not pan:
        return None
    digits = pan.replace(" ", "").replace("-", "")
    if len(digits) >= 4:
        return f"****-****-****-{digits[-4:]}"
    return "****"


def _to_customer_search_result(c: Any) -> CustomerSearchResult:
    return CustomerSearchResult(
        id=str(c["id"]),
        first_name=c["first_name"],
        last_name=c["last_name"],
        national_id=c["national_id"],
        mobile=c["mobile"],
        email=c["email"],
        status=c["status"],
        segment=c["segment"],
        branch_id=c["branch_id"],
    )


def _to_customer_detail(c: Any) -> CustomerDetailResponse:
    return CustomerDetailResponse(
        id=str(c["id"]),
        first_name=c["first_name"],
        last_name=c["last_name"],
        national_id=c["national_id"],
        mobile=c["mobile"],
        email=c["email"],
        status=c["status"],
        segment=c["segment"],
        branch_id=c["branch_id"],
        created_at=c["created_at"],
    )


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search_customers(
    cms_db: Session,
    *,
    q: Optional[str] = None,
    national_id: Optional[str] = None,
    status: Optional[str] = None,
    segment: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
) -> CustomerSearchResponse:

    business_db = get_business_db(cms_db)
    try:
        items, total = customer_repository.search(
            business_db,
            q=q,
            national_id=national_id,
            status=status,
            segment=segment,
            page=page,
            page_size=page_size,
        )
    except ValueError as exc:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    finally:
        business_db.close()

    pages: Optional[int] = None
    if total is not None and page_size > 0:
        pages = math.ceil(total / page_size)

    return CustomerSearchResponse(
        items=[_to_customer_search_result(c) for c in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


# ---------------------------------------------------------------------------
# Detail
# ---------------------------------------------------------------------------

def get_customer_detail(cms_db: Session, customer_id: str) -> CustomerDetailResponse:
    business_db = get_business_db(cms_db)
    try:
        customer = customer_repository.get_by_id(business_db, customer_id)
    finally:
        business_db.close()

    if not customer:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{customer_id}' not found.",
        )
    return _to_customer_detail(customer)


# ---------------------------------------------------------------------------
# Linked entities
# ---------------------------------------------------------------------------

def get_customer_contracts(cms_db: Session, customer_id: str) -> List[CustomerContractResponse]:
    business_db = get_business_db(cms_db)
    try:
        rows = customer_contract_repository.get_by_customer(business_db, customer_id)
    finally:
        business_db.close()
    return [CustomerContractResponse.model_validate(dict(r)) for r in rows]


def get_customer_cards(
    cms_db: Session,
    customer_id: str,
    *,
    include_pan: bool = False,
) -> List[CustomerCardResponse]:
    business_db = get_business_db(cms_db)
    try:
        rows = customer_card_repository.get_by_customer(business_db, customer_id)
    finally:
        business_db.close()

    result = []
    for r in rows:
        result.append(CustomerCardResponse(
            id=str(r["id"]),
            customer_id=str(r["customer_id"]),
            card_number_masked=_mask_card(r["card_number"]),
            card_number_clear=r["card_number"] if include_pan else None,
            card_type=r["card_type"],
            status=r["status"],
            expiry_date=r["expiry_date"],
        ))
    return result


def get_customer_accounts(
    cms_db: Session, customer_id: str, *, include_balance: bool
) -> List[CustomerAccountResponse]:
    business_db = get_business_db(cms_db)
    try:
        rows = customer_account_repository.get_by_customer(business_db, customer_id)
    finally:
        business_db.close()

    result = []
    for r in rows:
        result.append(CustomerAccountResponse(
            id=str(r["id"]),
            customer_id=str(r["customer_id"]),
            account_number=r["account_number"],
            currency=r["currency"],
            balance=r["balance"] if include_balance else None,
            status=r["status"],
        ))
    return result


def get_customer_documents(cms_db: Session, customer_id: str) -> List[CustomerDocumentResponse]:
    business_db = get_business_db(cms_db)
    try:
        rows = customer_document_repository.get_by_customer(business_db, customer_id)
    finally:
        business_db.close()
    return [CustomerDocumentResponse.model_validate(dict(r)) for r in rows]


def get_customer_contacts(cms_db: Session, customer_id: str) -> List[CustomerContactResponse]:
    business_db = get_business_db(cms_db)
    try:
        rows = customer_contact_repository.get_by_customer(business_db, customer_id)
    finally:
        business_db.close()
    return [CustomerContactResponse.model_validate(dict(r)) for r in rows]
