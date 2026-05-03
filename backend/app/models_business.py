"""
Business Database Models — Phase 05

These models map to read-only tables on the external Oracle (or PostgreSQL)
business database. Table names reflect the real Oracle schema (taly-dev-bo / MAIN).

Oracle table mapping:
  Customer        → MAIN.PRD_CUSTOMER
  CustomerContract→ MAIN.PRD_CONTRACT
  CustomerCard    → MAIN.ISS_CARD
  Cardholder      → MAIN.ISS_CARDHOLDER
  CustomerAccount → MAIN.ACC_BUSINESS_ACCOUNT (placeholder — not yet used)
  CustomerDocument→ MAIN.RPT_DOCUMENT         (placeholder — not yet used)
  CustomerContact → MAIN.COM_CONTACT_DATA     (placeholder — not yet used)

Note: Customer search uses raw SQL in the repository layer (JOIN across
PRD_CUSTOMER + ISS_CARD + ISS_CARDHOLDER) because a single customer can have
multiple cards. Schema prefix is extracted dynamically from the engine's
schema_translate_map execution option.
"""

import os
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Date,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

# Separate Base — never shared with CMS models
BusinessBase = declarative_base()

# Optional Oracle schema prefix (used as static fallback only)
_SCHEMA: str | None = os.getenv("BUSINESS_SCHEMA") or None


# ============================================================================
# CUSTOMER  (MAIN.PRD_CUSTOMER)
# ============================================================================

class Customer(BusinessBase):
    """Customer master record — maps to MAIN.PRD_CUSTOMER."""
    __tablename__ = "PRD_CUSTOMER"
    __table_args__ = {"schema": _SCHEMA} if _SCHEMA else {}

    id = Column("ID", Numeric, primary_key=True)
    customer_number = Column("CUSTOMER_NUMBER", String(100))
    status = Column("STATUS", String(30))
    category = Column("CATEGORY", String(50))
    entity_type = Column("ENTITY_TYPE", String(50))
    object_id = Column("OBJECT_ID", Numeric)
    nationality = Column("NATIONALITY", String(50))
    marital_status = Column("MARITAL_STATUS", String(50))
    reg_date = Column("REG_DATE", DateTime)
    employment_status = Column("EMPLOYMENT_STATUS", String(50))
    income_range = Column("INCOME_RANGE", String(50))


# ============================================================================
# CARDHOLDER  (MAIN.ISS_CARDHOLDER)
# ============================================================================

class Cardholder(BusinessBase):
    """Cardholder — maps to MAIN.ISS_CARDHOLDER. Holds the customer's name."""
    __tablename__ = "ISS_CARDHOLDER"
    __table_args__ = {"schema": _SCHEMA} if _SCHEMA else {}

    id = Column("ID", Numeric, primary_key=True)
    person_id = Column("PERSON_ID", Numeric)
    cardholder_number = Column("CARDHOLDER_NUMBER", String(100))
    cardholder_name = Column("CARDHOLDER_NAME", String(200))
    nationality = Column("NATIONALITY", String(50))
    marital_status = Column("MARITAL_STATUS", String(50))


# ============================================================================
# CARD  (MAIN.ISS_CARD)
# ============================================================================

class CustomerCard(BusinessBase):
    """Payment card — maps to MAIN.ISS_CARD.

    CARD_MASK may be a full PAN for test environments. Masking is applied
    at the SERVICE layer before returning to the API.
    """
    __tablename__ = "ISS_CARD"
    __table_args__ = {"schema": _SCHEMA} if _SCHEMA else {}

    id = Column("ID", Numeric, primary_key=True)
    customer_id = Column("CUSTOMER_ID", Numeric, index=True)
    cardholder_id = Column("CARDHOLDER_ID", Numeric, index=True)
    contract_id = Column("CONTRACT_ID", Numeric)
    card_mask = Column("CARD_MASK", String(25))     # PAN or masked PAN
    card_type_id = Column("CARD_TYPE_ID", Numeric)
    category = Column("CATEGORY", String(50))
    reg_date = Column("REG_DATE", DateTime)


# ============================================================================
# CONTRACT  (MAIN.PRD_CONTRACT)
# ============================================================================

class CustomerContract(BusinessBase):
    """Contract — maps to MAIN.PRD_CONTRACT."""
    __tablename__ = "PRD_CONTRACT"
    __table_args__ = {"schema": _SCHEMA} if _SCHEMA else {}

    id = Column("ID", Numeric, primary_key=True)
    customer_id = Column("CUSTOMER_ID", Numeric, index=True)
    contract_number = Column("CONTRACT_NUMBER", String(100))
    contract_type = Column("CONTRACT_TYPE", String(50))
    product_id = Column("PRODUCT_ID", Numeric)
    start_date = Column("START_DATE", Date)
    end_date = Column("END_DATE", Date)


# ============================================================================
# ACCOUNT  (placeholder — MAIN.ACC_BUSINESS_ACCOUNT)
# ============================================================================

class CustomerAccount(BusinessBase):
    """Bank account placeholder — not actively queried yet."""
    __tablename__ = "ACC_BUSINESS_ACCOUNT"
    __table_args__ = {"schema": _SCHEMA} if _SCHEMA else {}

    id = Column("ID", Numeric, primary_key=True)
    customer_id = Column("CUSTOMER_ID", Numeric, index=True)
    account_number = Column("ACCOUNT_NUMBER", String(50))
    currency = Column("CURRENCY", String(3))
    status = Column("STATUS", String(30))


# ============================================================================
# DOCUMENT  (placeholder — MAIN.RPT_DOCUMENT)
# ============================================================================

class CustomerDocument(BusinessBase):
    """Document placeholder — not actively queried yet."""
    __tablename__ = "RPT_DOCUMENT"
    __table_args__ = {"schema": _SCHEMA} if _SCHEMA else {}

    id = Column("ID", Numeric, primary_key=True)
    document_type = Column("DOCUMENT_TYPE", String(50))
    document_number = Column("DOCUMENT_NUMBER", String(100))


# ============================================================================
# CONTACT  (placeholder — MAIN.COM_CONTACT_DATA)
# ============================================================================

class CustomerContact(BusinessBase):
    """Contact placeholder — not actively queried yet."""
    __tablename__ = "COM_CONTACT_DATA"
    __table_args__ = {"schema": _SCHEMA} if _SCHEMA else {}

    id = Column("ID", Numeric, primary_key=True)
    contact_id = Column("CONTACT_ID", Numeric, index=True)
    commun_method = Column("COMMUN_METHOD", String(30))
    commun_address = Column("COMMUN_ADDRESS", String(300))
