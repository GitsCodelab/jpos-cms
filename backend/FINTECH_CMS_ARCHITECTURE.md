# Fintech CMS Platform - Architecture Guide

## Project Overview

**Purpose**: Reconciliation, Settlement Monitoring, Fraud Monitoring, Transaction Dashboards, Operational Management

**Architecture Pattern**: Service/Repository Layer + SQLAlchemy ORM + Pydantic Validation

**Technology Stack**:
- Backend: FastAPI + Uvicorn
- ORM: SQLAlchemy (supports PostgreSQL now, Oracle via cx_Oracle)
- Auth: JWT (Bearer token, HS256)
- Database: PostgreSQL (development), Oracle (production)

---

## Data Model Architecture

### 1. Core Domain Models

```
Transaction (from external source)
├── ID, Amount, Currency
├── Timestamp, Type (DEBIT/CREDIT)
├── External Reference
└── Status (NEW, MATCHED, UNMATCHED, RESOLVED)

SettlementBatch
├── ID, Date, Period
├── Reference, Status
└── Transactions (relationship)

ReconciliationRun
├── ID, RunDate, Period
├── Status (PENDING, IN_PROGRESS, MATCHED, UNMATCHED, RESOLVED)
├── MatchedCount, UnmatchedCount, ErrorCount
└── Transactions (relationship)

FraudAlert
├── ID, TransactionID, AlertDate
├── RuleTriggered, RiskScore (0-100)
├── Status (PENDING, REVIEWED, APPROVED, REJECTED)
└── Comment

SettlementStatement
├── ID, Date, Type
├── TotalAmount, TransactionCount
├── Status (DRAFT, FINALIZED, APPROVED)
└── Transactions (relationship)

ReportJob
├── ID, JobType, CreatedAt
├── Status (PENDING, PROCESSING, COMPLETED, FAILED)
├── Format (PDF, CSV, EXCEL)
└── DownloadURL
```

---

## API Endpoints Structure

### Authentication (Existing - DO NOT MODIFY)
```
POST   /auth/login              (public)
GET    /health                  (public)
GET    /ping                    (protected)
```

### Reconciliation API
```
GET    /api/reconciliation/runs              (list runs)
POST   /api/reconciliation/runs              (create run)
GET    /api/reconciliation/runs/{id}         (get details)
GET    /api/reconciliation/runs/{id}/matches (get matches)
GET    /api/reconciliation/runs/{id}/unmatches (get unmatches)
PATCH  /api/reconciliation/runs/{id}/resolve (mark resolved)
```

### Transactions API
```
GET    /api/transactions                     (list with filters)
GET    /api/transactions/{id}                (get detail)
GET    /api/transactions/search              (advanced search)
POST   /api/transactions/bulk-import         (from external source)
```

### Settlement API
```
GET    /api/settlement/batches               (list batches)
POST   /api/settlement/batches               (create batch)
GET    /api/settlement/batches/{id}          (get batch)
GET    /api/settlement/statements            (list statements)
POST   /api/settlement/statements            (generate statement)
```

### Fraud Monitoring API
```
GET    /api/fraud/alerts                     (list alerts)
GET    /api/fraud/alerts/{id}                (get alert)
PATCH  /api/fraud/alerts/{id}/review         (review alert)
GET    /api/fraud/rules                      (list rules)
POST   /api/fraud/rules                      (create rule)
```

### Reporting API
```
POST   /api/reports/generate                 (async job)
GET    /api/reports/jobs/{id}                (check status)
GET    /api/reports/jobs/{id}/download       (download file)
GET    /api/reports/reconciliation           (pre-built)
GET    /api/reports/settlement               (pre-built)
GET    /api/reports/fraud-summary            (pre-built)
```

### Dashboard/NET Settlement API
```
GET    /api/dashboard/summary                (dashboard metrics)
GET    /api/dashboard/alerts                 (recent alerts)
GET    /api/net-settlement/positions         (settlement positions)
GET    /api/net-settlement/daily-summary     (daily NET calculation)
```

---

## Service Layer Architecture

```
routers/
├── __init__.py
├── auth.py                 (EXISTING - DO NOT MODIFY)
├── reconciliation.py       (NEW)
├── transactions.py         (NEW)
├── settlement.py           (NEW)
├── fraud.py               (NEW)
├── reporting.py           (NEW)
├── dashboard.py           (NEW)
└── net.py                 (NEW)

services/
├── __init__.py
├── reconciliation_service.py   (match logic, state machine)
├── transaction_service.py      (query, filter, aggregate)
├── settlement_service.py       (batch calc, NET settlement)
├── fraud_service.py            (rule engine, scoring)
└── reporting_service.py        (async job handling)

repositories/
├── __init__.py
├── base_repository.py          (generic CRUD + Oracle support)
├── transaction_repository.py
├── reconciliation_repository.py
├── fraud_repository.py
├── settlement_repository.py
└── report_repository.py

schemas/
├── __init__.py
├── transaction.py             (request/response models)
├── reconciliation.py
├── fraud.py
├── settlement.py
└── reporting.py

models/
├── __init__.py
├── transaction.py             (SQLAlchemy ORM)
├── reconciliation.py
├── fraud.py
├── settlement.py
└── reporting.py
```

---

## Design Principles

### 1. Reconciliation Architecture
- **State Machine**: PENDING → IN_PROGRESS → MATCHED/UNMATCHED → RESOLVED
- **Match Logic**: Amount + Reference + Timestamp (within tolerance)
- **Audit Trail**: Track all state changes with timestamps and user IDs
- **Performance**: Index on status, date ranges, external references

### 2. Oracle Access Patterns
- **Connection Pooling**: SQLAlchemy engine with pool_pre_ping + pool_recycle
- **Parameterized Queries**: Prevent SQL injection (SQLAlchemy handles)
- **Batch Operations**: Use ORM bulk_insert_mappings for 1000+ row inserts
- **Read Replicas**: Query service layer can support fallback to read replica
- **Prepared Statements**: Oracle-specific optimization via cx_Oracle native SQL

### 3. Transaction Querying
- **Filtering**: By date range, amount, currency, status, type, external_ref
- **Pagination**: Offset/limit with cursor support for large datasets
- **Aggregation**: Sum, count, average by period/type/currency
- **Full-Text Search**: Transaction reference, description (Oracle CONTAINS)
- **Export**: CSV, Excel with configurable columns

### 4. Reporting Services
- **Async Queue**: Celery or RQ for long-running reports
- **Templating**: Jinja2 for report layouts
- **Export Formats**: PDF (ReportLab), CSV, Excel (openpyxl), JSON
- **Caching**: Redis for frequently-run reports
- **Webhooks**: Notify when report completes

### 5. Fraud Monitoring APIs
- **Rule Engine**: Declarative rules (amount > X, velocity > Y, geo-mismatch, etc.)
- **Scoring Algorithm**: Sum of rule weights → risk_score (0-100)
- **Alert Thresholds**: LOW (0-33), MEDIUM (34-66), HIGH (67-100)
- **Feedback Loop**: Reviewer decisions train future rules
- **Real-time Alerts**: Webhook to external fraud system

### 6. Preserve Existing Endpoints
- ✓ /auth/login (JWT generation)
- ✓ /health (service health)
- ✓ /ping (protected, requires Bearer token)
- **Version**: All new endpoints are /api/v1/* (future-proof)

---

## Database Indexes (Oracle/PostgreSQL)

```sql
-- Transactions (high volume)
CREATE INDEX idx_transactions_date ON transactions(created_at DESC);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_reference ON transactions(external_reference);
CREATE INDEX idx_transactions_reconciliation_run ON transactions(reconciliation_run_id);

-- Reconciliation Runs
CREATE INDEX idx_recon_runs_date ON reconciliation_runs(run_date DESC);
CREATE INDEX idx_recon_runs_status ON reconciliation_runs(status);

-- Fraud Alerts
CREATE INDEX idx_fraud_alerts_date ON fraud_alerts(alert_date DESC);
CREATE INDEX idx_fraud_alerts_status ON fraud_alerts(status);
CREATE INDEX idx_fraud_alerts_transaction ON fraud_alerts(transaction_id);

-- Settlement Batches
CREATE INDEX idx_settlement_batches_date ON settlement_batches(batch_date DESC);
CREATE INDEX idx_settlement_batches_period ON settlement_batches(settlement_period);

-- Composite Indexes for common queries
CREATE INDEX idx_transactions_date_status ON transactions(created_at DESC, status);
CREATE INDEX idx_transactions_reconciliation_date ON transactions(reconciliation_run_id, created_at);
```

---

## Configuration (Environment Variables)

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/jpos_cms
# For Oracle: oracle+cx_oracle://user:pass@oracle_host:1521/?service_name=xepdb1
ORACLE_HOST=
ORACLE_PORT=1521
ORACLE_USER=
ORACLE_PASSWORD=
ORACLE_SERVICE_NAME=

# JWT (existing)
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Fraud Rules
FRAUD_ALERT_WEBHOOK_URL=https://fraud-system/alerts

# Reporting
REPORT_TEMP_DIR=/tmp/reports
REPORT_RETENTION_DAYS=30

# Feature Flags
ENABLE_ORACLE_REPORTING=false
ENABLE_FRAUD_WEBHOOKS=false
```

---

## Implementation Roadmap

**Phase 1: Data Models & Database**
- [ ] SQLAlchemy models for all entities
- [ ] Alembic migrations
- [ ] Test database setup

**Phase 2: Service Layer**
- [ ] Base repository pattern
- [ ] Reconciliation service (match logic)
- [ ] Transaction service (query/filter)
- [ ] Tests for services

**Phase 3: API Endpoints**
- [ ] Reconciliation API
- [ ] Transactions API
- [ ] Settlement API
- [ ] Integration tests

**Phase 4: Advanced Features**
- [ ] Fraud monitoring service + API
- [ ] Reporting service (async)
- [ ] Dashboard endpoints
- [ ] NET settlement calculations

**Phase 5: Oracle Integration**
- [ ] Update DATABASE_URL to Oracle
- [ ] Performance testing
- [ ] Index optimization

**Phase 6: Production Readiness**
- [ ] Logging & monitoring
- [ ] Error handling
- [ ] Rate limiting
- [ ] API documentation

---

## Testing Strategy

```
tests/
├── test_reconciliation_service.py    (unit tests)
├── test_transaction_service.py
├── test_fraud_service.py
├── test_reconciliation_api.py        (integration tests)
├── test_transactions_api.py
├── conftest.py                       (fixtures, test DB)
└── test_data/                        (sample data)
```

Use pytest + pytest-asyncio for async endpoint testing.

---

## Next Steps

1. Read this document
2. Implement Phase 1: Data models
3. Implement Phase 2: Service layer
4. Implement Phase 3: API endpoints
5. Add tests and documentation
