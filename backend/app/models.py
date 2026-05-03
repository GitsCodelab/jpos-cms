"""
SQLAlchemy ORM Models for Fintech CMS Platform

Supports both PostgreSQL and Oracle via SQLAlchemy + cx_Oracle driver.
All models include:
- Timestamps (created_at, updated_at)
- Status tracking for state machines
- Foreign key relationships
- Composite indexes defined in database layer
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref

from app.db import Base


# ============================================================================
# ENUMS: Represent state machines and categorical values
# ============================================================================


class TransactionStatus(str, PyEnum):
    """Transaction lifecycle: NEW → MATCHED/UNMATCHED → RESOLVED"""
    NEW = "NEW"
    MATCHED = "MATCHED"
    UNMATCHED = "UNMATCHED"
    RESOLVED = "RESOLVED"


class TransactionType(str, PyEnum):
    """Transaction direction"""
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class ReconciliationStatus(str, PyEnum):
    """Reconciliation run lifecycle"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    MATCHED = "MATCHED"
    UNMATCHED = "UNMATCHED"
    RESOLVED = "RESOLVED"


class FraudAlertStatus(str, PyEnum):
    """Fraud alert lifecycle"""
    PENDING = "PENDING"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class FraudRiskLevel(str, PyEnum):
    """Fraud risk classification"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class SettlementStatus(str, PyEnum):
    """Settlement batch/statement lifecycle"""
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    FINALIZED = "FINALIZED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ReportStatus(str, PyEnum):
    """Report generation job status"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ReportFormat(str, PyEnum):
    """Export format for reports"""
    PDF = "PDF"
    CSV = "CSV"
    EXCEL = "EXCEL"
    JSON = "JSON"


# ============================================================================
# TRANSACTION MODEL
# ============================================================================


class Transaction(Base):
    """
    Transaction record (from jPOS switch or external source).
    
    High-volume table: ~1M rows per month
    Key indexes: date, status, reference, reconciliation_run_id
    """
    __tablename__ = "transactions"

    id = Column(String(50), primary_key=True)  # UUID
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)  # USD, EUR, etc.
    transaction_type = Column(Enum(TransactionType), nullable=False)
    external_reference = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    
    # Source and status tracking
    source_system = Column(String(50))  # jPOS, SWIFT, etc.
    status = Column(Enum(TransactionStatus), default=TransactionStatus.NEW, nullable=False)
    
    # Timestamps
    transaction_date = Column(DateTime, nullable=False)  # When transaction occurred
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reconciliation_run_id = Column(String(50), ForeignKey("reconciliation_runs.id"))
    settlement_batch_id = Column(String(50), ForeignKey("settlement_batches.id"))
    fraud_alert_id = Column(String(50), ForeignKey("fraud_alerts.id"))
    
    reconciliation_run = relationship("ReconciliationRun", back_populates="transactions")
    settlement_batch = relationship("SettlementBatch", back_populates="transactions")
    fraud_alert = relationship("FraudAlert", foreign_keys="[FraudAlert.transaction_id]", uselist=False, back_populates="transaction")
    
    # Indexes for common queries
    __table_args__ = (
        Index("idx_transactions_date", "transaction_date"),
        Index("idx_transactions_status", "status"),
        Index("idx_transactions_reference", "external_reference"),
        Index("idx_transactions_reconciliation_run", "reconciliation_run_id"),
        Index("idx_transactions_date_status", "transaction_date", "status"),
    )


# ============================================================================
# RECONCILIATION MODEL
# ============================================================================


class ReconciliationRun(Base):
    """
    Reconciliation run: compares transactions across sources.
    
    Typical flow:
    1. Create run (PENDING)
    2. Load transactions (IN_PROGRESS)
    3. Match them (MATCHED state)
    4. Identify unmatches (UNMATCHED state)
    5. Resolve all (RESOLVED)
    """
    __tablename__ = "reconciliation_runs"

    id = Column(String(50), primary_key=True)  # UUID
    run_date = Column(DateTime, nullable=False)
    settlement_period = Column(String(20))  # "2026-05-01"
    
    # Matching results
    status = Column(Enum(ReconciliationStatus), default=ReconciliationStatus.PENDING, nullable=False)
    matched_count = Column(Integer, default=0)
    unmatched_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    # Matching tolerance (for fuzzy matching)
    amount_tolerance = Column(Float, default=0.01)  # cents
    date_tolerance_days = Column(Integer, default=1)
    
    # Metadata
    notes = Column(Text)
    created_by = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="reconciliation_run")
    unmatches = relationship("ReconciliationUnmatch", back_populates="reconciliation_run")
    
    __table_args__ = (
        Index("idx_recon_runs_date", "run_date"),
        Index("idx_recon_runs_status", "status"),
        Index("idx_recon_runs_period", "settlement_period"),
    )


class ReconciliationUnmatch(Base):
    """
    Unmatched transaction record during reconciliation.
    
    Used for investigation and manual resolution.
    """
    __tablename__ = "reconciliation_unmatches"

    id = Column(String(50), primary_key=True)  # UUID
    reconciliation_run_id = Column(String(50), ForeignKey("reconciliation_runs.id"), nullable=False)
    
    transaction_id = Column(String(50), ForeignKey("transactions.id"))
    external_transaction_id = Column(String(50))  # If matched to external system
    
    amount_difference = Column(Float)
    date_difference_days = Column(Integer)
    reason = Column(String(200))  # Amount mismatch, Date mismatch, Missing from external, etc.
    
    resolution_status = Column(String(50))  # PENDING, RESOLVED, ESCALATED
    resolved_at = Column(DateTime)
    resolved_by = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    reconciliation_run = relationship("ReconciliationRun", back_populates="unmatches")


# ============================================================================
# FRAUD MONITORING MODELS
# ============================================================================


class FraudRule(Base):
    """
    Fraud detection rule (declarative).
    
    Example:
    - name: "High Amount Debit"
    - condition: "amount > 100000 AND transaction_type == 'DEBIT'"
    - weight: 25 (contributes to overall risk score)
    - enabled: true
    """
    __tablename__ = "fraud_rules"

    id = Column(String(50), primary_key=True)  # UUID
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    
    # Rule definition
    condition = Column(Text, nullable=False)  # e.g., "amount > 100000"
    weight = Column(Float, default=10.0)  # Contribution to risk score (0-100)
    
    # Rule management
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Higher = checked first
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(50))


class FraudAlert(Base):
    """
    Fraud alert generated when transaction triggers rules.
    
    Risk score is sum of triggered rule weights (0-100).
    """
    __tablename__ = "fraud_alerts"

    id = Column(String(50), primary_key=True)  # UUID
    transaction_id = Column(String(50), ForeignKey("transactions.id"), nullable=False, unique=True)
    
    # Risk calculation
    risk_score = Column(Float, default=0.0)  # 0-100
    risk_level = Column(Enum(FraudRiskLevel), nullable=False)
    triggered_rules = Column(Text)  # JSON array of rule IDs
    
    # Alert lifecycle
    status = Column(Enum(FraudAlertStatus), default=FraudAlertStatus.PENDING, nullable=False)
    reviewed_at = Column(DateTime)
    reviewed_by = Column(String(50))
    
    # Resolution
    resolution_comment = Column(Text)
    
    # Timestamps
    alert_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    transaction = relationship("Transaction", foreign_keys=[transaction_id], back_populates="fraud_alert")
    
    __table_args__ = (
        Index("idx_fraud_alerts_date", "alert_date"),
        Index("idx_fraud_alerts_status", "status"),
        Index("idx_fraud_alerts_transaction", "transaction_id"),
    )


# ============================================================================
# SETTLEMENT MODELS
# ============================================================================


class SettlementBatch(Base):
    """
    Settlement batch: groups transactions for settlement processing.
    
    Example: Daily batch for USD transactions on 2026-05-01
    """
    __tablename__ = "settlement_batches"

    id = Column(String(50), primary_key=True)  # UUID
    batch_date = Column(DateTime, nullable=False)  # When batch was created
    settlement_period = Column(String(20), nullable=False)  # "2026-05-01"
    
    currency = Column(String(3), nullable=False)  # USD, EUR, etc.
    status = Column(Enum(SettlementStatus), default=SettlementStatus.DRAFT, nullable=False)
    
    # Settlement calculation
    total_amount = Column(Float, default=0.0)
    transaction_count = Column(Integer, default=0)
    debit_amount = Column(Float, default=0.0)
    credit_amount = Column(Float, default=0.0)
    
    # NET settlement (debit - credit)
    net_amount = Column(Float, default=0.0)
    net_direction = Column(String(10))  # DEBIT, CREDIT
    
    reference = Column(String(100))
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    finalized_at = Column(DateTime)
    
    transactions = relationship("Transaction", back_populates="settlement_batch")
    
    __table_args__ = (
        Index("idx_settlement_batches_date", "batch_date"),
        Index("idx_settlement_batches_period", "settlement_period"),
        Index("idx_settlement_batches_status", "status"),
    )


class SettlementStatement(Base):
    """
    Settlement statement: formal document confirming settlement.
    
    Contains summary of all batches for a period.
    """
    __tablename__ = "settlement_statements"

    id = Column(String(50), primary_key=True)  # UUID
    statement_date = Column(DateTime, nullable=False)
    settlement_period = Column(String(20), nullable=False)  # "2026-05-01"
    
    status = Column(Enum(SettlementStatus), default=SettlementStatus.DRAFT, nullable=False)
    
    # Aggregated summary
    total_transactions = Column(Integer, default=0)
    total_amount = Column(Float, default=0.0)
    total_debit_amount = Column(Float, default=0.0)
    total_credit_amount = Column(Float, default=0.0)
    net_settlement = Column(Float, default=0.0)
    
    # Content
    statement_reference = Column(String(100))
    file_path = Column(String(255))  # Path to generated PDF/Excel
    
    # Approval workflow
    prepared_by = Column(String(50))
    approved_by = Column(String(50))
    approved_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    finalized_at = Column(DateTime)


# ============================================================================
# REPORTING MODELS
# ============================================================================


class ReportJob(Base):
    """
    Async report generation job.
    
    User requests report → creates job → background task processes → file ready for download
    """
    __tablename__ = "report_jobs"

    id = Column(String(50), primary_key=True)  # UUID
    report_type = Column(String(50), nullable=False)  # reconciliation, settlement, fraud, etc.
    
    # Parameters
    settlement_period = Column(String(20))  # "2026-05-01"
    date_from = Column(DateTime)
    date_to = Column(DateTime)
    filters = Column(Text)  # JSON with additional filters
    
    # Execution
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, nullable=False)
    format = Column(Enum(ReportFormat), default=ReportFormat.PDF, nullable=False)
    
    # Output
    file_path = Column(String(255))  # Where generated file is stored
    file_size_bytes = Column(Integer)
    error_message = Column(Text)  # If status == FAILED
    
    # Metadata
    requested_by = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Retention
    expires_at = Column(DateTime)  # Auto-delete old reports
    
    __table_args__ = (
        Index("idx_report_jobs_status", "status"),
        Index("idx_report_jobs_created", "created_at"),
        Index("idx_report_jobs_type", "report_type"),
    )


# ============================================================================
# AUTHENTICATION MODELS: User, Session, and Audit
# ============================================================================


class User(Base):
    """
    User account model for authentication.
    
    Supports:
    - Multiple users with individual passwords
    - Role-based access control (RBAC)
    - Account activation/deactivation
    - Password hashing via bcrypt
    - Session tracking
    """
    __tablename__ = "users"
    
    # Primary key
    id = Column(String(50), primary_key=True)
    
    # Credentials
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # bcrypt hash (60 chars)
    
    # Profile
    email = Column(String(150), unique=True, index=True)
    full_name = Column(String(200))
    
    # Authorization
    role = Column(String(50), default="user", nullable=False)  # admin, user, manager, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
    last_password_change = Column(DateTime)
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    login_audits = relationship("LoginAudit", back_populates="user")
    
    __table_args__ = (
        Index("idx_users_username", "username"),
        Index("idx_users_email", "email"),
        Index("idx_users_is_active", "is_active"),
    )
    
    def __repr__(self):
        return f"<User username={self.username} role={self.role}>"


class UserSession(Base):
    """
    Active user sessions tracking.
    
    Allows:
    - Viewing all active sessions for a user
    - Revoking specific sessions (logout on other devices)
    - Tracking login location/device
    - Automatic expiry of stale sessions
    """
    __tablename__ = "user_sessions"
    
    # Primary key
    id = Column(String(50), primary_key=True)
    
    # Relationship
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="sessions")
    
    # Token tracking
    token_jti = Column(String(100), unique=True, index=True)  # JWT ID
    
    # Location tracking
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    # Status
    revoked = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime)
    
    __table_args__ = (
        Index("idx_user_sessions_user_id", "user_id"),
        Index("idx_user_sessions_token_jti", "token_jti"),
        Index("idx_user_sessions_expires", "expires_at"),
        Index("idx_user_sessions_revoked", "revoked"),
    )
    
    def __repr__(self):
        return f"<UserSession user_id={self.user_id} jti={self.token_jti[:10]}...>"


class LoginAudit(Base):
    """
    Login attempt audit trail.
    
    Records all login attempts (successful and failed) for:
    - Security monitoring
    - Compliance/audit requirements
    - Detecting brute force attacks
    - Geographic anomalies
    """
    __tablename__ = "login_audit"
    
    # Primary key
    id = Column(String(50), primary_key=True)
    
    # User reference (denormalized for failed logins)
    username = Column(String(100), nullable=False, index=True)
    user_id = Column(String(50), ForeignKey("users.id", ondelete="SET NULL"))
    user = relationship("User", back_populates="login_audits")
    
    # Request details
    ip_address = Column(String(50), index=True)
    user_agent = Column(String(500))
    
    # Result
    success = Column(Boolean, nullable=False, index=True)
    failure_reason = Column(String(200))  # e.g., "Invalid credentials", "Account locked"
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index("idx_login_audit_username_timestamp", "username", "timestamp"),
        Index("idx_login_audit_ip_timestamp", "ip_address", "timestamp"),
        Index("idx_login_audit_success", "success"),
    )
    
    def __repr__(self):
        status = "✓" if self.success else "✗"
        return f"<LoginAudit {status} {self.username} {self.timestamp}>"


class TokenBlacklist(Base):
    """
    Revoked JWT tokens tracking.
    
    Prevents reuse of:
    - Tokens after logout
    - Tokens after password change
    - Tokens after role change
    - All tokens after account suspension
    """
    __tablename__ = "token_blacklist"
    
    # Primary key
    id = Column(String(50), primary_key=True)
    
    # Token details
    jti = Column(String(100), unique=True, nullable=False, index=True)  # JWT ID
    username = Column(String(100), nullable=False, index=True)
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"))
    
    # Reason for blacklisting
    reason = Column(String(200), nullable=False)  # logout, password_change, role_change, admin_revoke, account_suspended
    
    # Token expiry (for cleanup)
    token_expires_at = Column(DateTime, nullable=False)
    
    # Blacklist metadata
    blacklisted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    blacklisted_by = Column(String(100))  # admin who blacklisted, if manual
    
    __table_args__ = (
        Index("idx_token_blacklist_jti", "jti"),
        Index("idx_token_blacklist_username", "username"),
        Index("idx_token_blacklist_expires", "token_expires_at"),
    )


# ============================================================================
# DATABASE CONNECTIONS MODEL
# ============================================================================


class DatabaseConnectionType(str, PyEnum):
    """Supported external database types"""
    ORACLE = "ORACLE"
    POSTGRESQL = "POSTGRESQL"


class DatabaseConnection(Base):
    """
    External database connection configuration.

    Stores connection details for Oracle and PostgreSQL databases used by:
    - reconciliation services
    - reporting services
    - fraud monitoring queries
    - operational dashboards

    Passwords are stored encrypted (Fernet symmetric encryption).
    """
    __tablename__ = "database_connections"

    id = Column(String(50), primary_key=True)  # UUID
    connection_name = Column(String(100), nullable=False, unique=True)
    database_type = Column(Enum(DatabaseConnectionType), nullable=False)

    # Connection parameters
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    service_name = Column(String(100), nullable=False)  # database name or Oracle service name
    username = Column(String(100), nullable=False)
    encrypted_password = Column(Text, nullable=False)  # Fernet-encrypted
    schema_name = Column(String(100))

    # Metadata
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_db_connections_name", "connection_name"),
        Index("idx_db_connections_type", "database_type"),
        Index("idx_db_connections_active", "is_active"),
    )

    def __repr__(self):
        return f"<DatabaseConnection name={self.connection_name} type={self.database_type}>"


# ============================================================================
# MENU PROFILE MODELS
# ============================================================================


class MenuProfile(Base):
    """
    Menu layout profile definition.

    Predefined profiles control which menu items appear in the sidebar.
    Only one profile can be the system default.
    Users can select their preferred profile.
    """
    __tablename__ = "menu_profiles"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)          # e.g. 'standard'
    display_name = Column(String(200), nullable=False)               # e.g. 'Standard'
    description = Column(Text)
    is_default = Column(Boolean, default=False, nullable=False)      # exactly one default
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile_menu_items = relationship(
        "ProfileMenuItem", back_populates="profile", cascade="all, delete-orphan"
    )
    user_profiles = relationship("UserMenuProfile", back_populates="profile")

    __table_args__ = (
        Index("idx_menu_profiles_name", "name"),
        Index("idx_menu_profiles_default", "is_default"),
    )

    def __repr__(self):
        return f"<MenuProfile name={self.name} default={self.is_default}>"


class MenuItem(Base):
    """
    Individual menu item in the navigation tree.

    Supports arbitrary depth via self-referential parent_id.
    Group items (is_group=True) have children but no route.
    Leaf items start with '/' and represent actual routes.
    icon_name stores the Ant Design icon component name as a string.
    """
    __tablename__ = "menu_items"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String(200), unique=True, nullable=False)           # route key e.g. '/issuing/cards'
    label = Column(String(200), nullable=False)
    icon_name = Column(String(100))                                  # e.g. 'CreditCardOutlined'
    permission = Column(String(200))
    parent_id = Column(String(50), ForeignKey("menu_items.id"), nullable=True)
    order_index = Column(Integer, default=0, nullable=False)
    is_group = Column(Boolean, default=False, nullable=False)        # True if has children
    is_active = Column(Boolean, default=True, nullable=False)        # Soft-disable without deleting

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    children = relationship(
        "MenuItem",
        foreign_keys=[parent_id],
        backref=backref("parent", remote_side="MenuItem.id"),
        order_by="MenuItem.order_index",
    )
    profile_menu_items = relationship("ProfileMenuItem", back_populates="menu_item")

    __table_args__ = (
        Index("idx_menu_items_key", "key"),
        Index("idx_menu_items_parent", "parent_id"),
    )

    def __repr__(self):
        return f"<MenuItem key={self.key} label={self.label}>"


class ProfileMenuItem(Base):
    """
    Association between a MenuProfile and a top-level MenuItem.

    Only top-level items (parent_id=None) are linked directly to profiles.
    Child items are reached through the MenuItem tree.
    """
    __tablename__ = "profile_menu_items"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(50), ForeignKey("menu_profiles.id"), nullable=False)
    menu_item_id = Column(String(50), ForeignKey("menu_items.id"), nullable=False)
    order_index = Column(Integer, default=0, nullable=False)

    profile = relationship("MenuProfile", back_populates="profile_menu_items")
    menu_item = relationship("MenuItem", back_populates="profile_menu_items")

    __table_args__ = (
        UniqueConstraint("profile_id", "menu_item_id", name="uq_profile_menu_item"),
        Index("idx_profile_menu_items_profile", "profile_id"),
    )


class UserMenuProfile(Base):
    """
    Records which MenuProfile a specific user has selected.

    One row per user. Missing row means user gets the default profile.
    """
    __tablename__ = "user_menu_profiles"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    profile_id = Column(String(50), ForeignKey("menu_profiles.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
    profile = relationship("MenuProfile", back_populates="user_profiles")

    __table_args__ = (
        Index("idx_user_menu_profiles_user", "user_id"),
    )

