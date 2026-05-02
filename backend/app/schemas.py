"""
Pydantic request/response schemas for API validation and documentation.

These schemas define the contract between frontend and backend.
Used in FastAPI route definitions for automatic validation and OpenAPI docs.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr

from app.models import (
    FraudAlertStatus,
    FraudRiskLevel,
    ReportFormat,
    ReportStatus,
    ReconciliationStatus,
    SettlementStatus,
    TransactionStatus,
    TransactionType,
)


# ============================================================================
# TRANSACTION SCHEMAS
# ============================================================================


class TransactionBase(BaseModel):
    """Common transaction fields"""
    amount: float = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    transaction_type: TransactionType
    external_reference: str
    description: Optional[str] = None
    source_system: Optional[str] = None


class TransactionCreate(TransactionBase):
    """Create transaction request"""
    transaction_date: datetime


class TransactionUpdate(BaseModel):
    """Update transaction (limited fields)"""
    status: Optional[TransactionStatus] = None
    description: Optional[str] = None


class TransactionResponse(TransactionBase):
    """Transaction response"""
    id: str
    status: TransactionStatus
    transaction_date: datetime
    created_at: datetime
    updated_at: datetime
    reconciliation_run_id: Optional[str] = None
    settlement_batch_id: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# RECONCILIATION SCHEMAS
# ============================================================================


class ReconciliationRunBase(BaseModel):
    """Common reconciliation run fields"""
    settlement_period: str  # "2026-05-01"
    amount_tolerance: float = Field(default=0.01, ge=0)
    date_tolerance_days: int = Field(default=1, ge=0)
    notes: Optional[str] = None


class ReconciliationRunCreate(ReconciliationRunBase):
    """Create reconciliation run request"""
    pass


class ReconciliationRunUpdate(BaseModel):
    """Update reconciliation run"""
    status: Optional[ReconciliationStatus] = None
    notes: Optional[str] = None


class ReconciliationRunResponse(ReconciliationRunBase):
    """Reconciliation run response"""
    id: str
    status: ReconciliationStatus
    matched_count: int
    unmatched_count: int
    error_count: int
    run_date: datetime
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


class ReconciliationSummary(BaseModel):
    """Summary of reconciliation results"""
    total_transactions: int
    matched_count: int
    unmatched_count: int
    error_count: int
    match_rate: float  # percentage


class ReconciliationUnmatchResponse(BaseModel):
    """Unmatched transaction detail"""
    id: str
    transaction_id: Optional[str]
    external_transaction_id: Optional[str]
    amount_difference: Optional[float]
    date_difference_days: Optional[int]
    reason: Optional[str]
    resolution_status: Optional[str]
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# FRAUD SCHEMAS
# ============================================================================


class FraudRuleBase(BaseModel):
    """Common fraud rule fields"""
    name: str
    description: Optional[str] = None
    condition: str  # e.g., "amount > 100000"
    weight: float = Field(default=10.0, ge=0, le=100)
    priority: int = Field(default=0, ge=0)
    enabled: bool = True


class FraudRuleCreate(FraudRuleBase):
    """Create fraud rule request"""
    pass


class FraudRuleResponse(FraudRuleBase):
    """Fraud rule response"""
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


class FraudAlertBase(BaseModel):
    """Common fraud alert fields"""
    risk_score: float = Field(default=0.0, ge=0, le=100)
    risk_level: FraudRiskLevel
    triggered_rules: Optional[str] = None


class FraudAlertResponse(FraudAlertBase):
    """Fraud alert response"""
    id: str
    transaction_id: str
    status: FraudAlertStatus
    alert_date: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    resolution_comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FraudAlertUpdate(BaseModel):
    """Update fraud alert (review/resolution)"""
    status: Optional[FraudAlertStatus] = None
    resolution_comment: Optional[str] = None


class FraudAlertSummary(BaseModel):
    """Fraud summary for dashboard"""
    total_alerts: int
    pending_alerts: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    average_risk_score: float


# ============================================================================
# SETTLEMENT SCHEMAS
# ============================================================================


class SettlementBatchBase(BaseModel):
    """Common settlement batch fields"""
    settlement_period: str  # "2026-05-01"
    currency: str = Field(min_length=3, max_length=3)
    notes: Optional[str] = None


class SettlementBatchCreate(SettlementBatchBase):
    """Create settlement batch request"""
    pass


class SettlementBatchUpdate(BaseModel):
    """Update settlement batch"""
    status: Optional[SettlementStatus] = None
    notes: Optional[str] = None


class SettlementBatchResponse(SettlementBatchBase):
    """Settlement batch response"""
    id: str
    status: SettlementStatus
    batch_date: datetime
    total_amount: float
    transaction_count: int
    debit_amount: float
    credit_amount: float
    net_amount: float
    net_direction: Optional[str]
    reference: Optional[str]
    created_at: datetime
    updated_at: datetime
    finalized_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SettlementStatementBase(BaseModel):
    """Common settlement statement fields"""
    settlement_period: str
    statement_reference: Optional[str] = None


class SettlementStatementCreate(SettlementStatementBase):
    """Create settlement statement request"""
    pass


class SettlementStatementResponse(SettlementStatementBase):
    """Settlement statement response"""
    id: str
    statement_date: datetime
    status: SettlementStatus
    total_transactions: int
    total_amount: float
    total_debit_amount: float
    total_credit_amount: float
    net_settlement: float
    file_path: Optional[str] = None
    prepared_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NETSettlementPosition(BaseModel):
    """NET settlement position for daily summary"""
    currency: str
    debit_total: float
    credit_total: float
    net_amount: float
    net_direction: str  # DEBIT or CREDIT
    batch_count: int


# ============================================================================
# REPORTING SCHEMAS
# ============================================================================


class ReportJobBase(BaseModel):
    """Common report job fields"""
    report_type: str
    settlement_period: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    filters: Optional[str] = None  # JSON string


class ReportJobCreate(ReportJobBase):
    """Create report job request"""
    format: ReportFormat = ReportFormat.PDF


class ReportJobResponse(ReportJobBase):
    """Report job response"""
    id: str
    status: ReportStatus
    format: ReportFormat
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    error_message: Optional[str] = None
    requested_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# DASHBOARD SCHEMAS
# ============================================================================


class DashboardSummary(BaseModel):
    """Dashboard overview metrics"""
    total_transactions_today: int
    total_amount_today: float
    
    # Reconciliation
    pending_reconciliation_runs: int
    matched_percentage: float
    
    # Fraud
    fraud_alerts_pending: int
    high_risk_alerts: int
    
    # Settlement
    pending_settlements: int
    net_settlement_amount: float
    
    # System
    last_update: datetime


class DashboardAlert(BaseModel):
    """Recent alert for dashboard"""
    id: str
    alert_type: str  # fraud, settlement, reconciliation
    severity: str  # high, medium, low
    message: str
    created_at: datetime
    transaction_id: Optional[str] = None


# ============================================================================
# LIST RESPONSES (with pagination)
# ============================================================================


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    total: int
    limit: int
    offset: int
    has_more: bool


class PaginatedTransactionResponse(BaseModel):
    """Paginated transaction list"""
    data: List[TransactionResponse]
    meta: PaginationMeta


class PaginatedReconciliationRunResponse(BaseModel):
    """Paginated reconciliation run list"""
    data: List[ReconciliationRunResponse]
    meta: PaginationMeta


class PaginatedFraudAlertResponse(BaseModel):
    """Paginated fraud alert list"""
    data: List[FraudAlertResponse]
    meta: PaginationMeta


class PaginatedSettlementBatchResponse(BaseModel):
    """Paginated settlement batch list"""
    data: List[SettlementBatchResponse]
    meta: PaginationMeta


class PaginatedReportJobResponse(BaseModel):
    """Paginated report job list"""
    data: List[ReportJobResponse]
    meta: PaginationMeta


# ============================================================================
# AUTHENTICATION SCHEMAS
# ============================================================================


class LoginRequest(BaseModel):
    """Login request"""
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=100)


class LoginResponse(BaseModel):
    """Login response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: dict = Field(..., description="User info")


class LogoutRequest(BaseModel):
    """Logout request"""
    pass


class LogoutResponse(BaseModel):
    """Logout response"""
    message: str = "Successfully logged out"


class UserProfileResponse(BaseModel):
    """Current user profile response"""
    username: str
    email: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    token_expires_at: datetime


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, description="At least 8 characters")


class ChangePasswordResponse(BaseModel):
    """Change password response"""
    message: str = "Password changed successfully"
    token_revocation_message: str = "All active sessions have been revoked for security"


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Refresh token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class CreateUserRequest(BaseModel):
    """Create new user request"""
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, description="At least 8 characters")
    email: str
    role: str = Field(default="user", description="admin|user")


class UserResponse(BaseModel):
    """User response"""
    id: str
    username: str
    email: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ActiveSessionResponse(BaseModel):
    """Active session info"""
    id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class LoginAuditResponse(BaseModel):
    """Login audit record"""
    id: str
    username: str
    success: bool
    failure_reason: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

