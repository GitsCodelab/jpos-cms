# Fintech CMS API Specification

**Version**: 1.0.0  
**Status**: Phase 3 - To Be Implemented  
**Base Path**: `/api` (all endpoints require Bearer token)

---

## Authentication

All endpoints (except `/auth/login` and `/health`) require JWT Bearer token:

```
Authorization: Bearer <token>
```

Token obtained from: `POST /auth/login` with admin/admin123 credentials.

---

## Reconciliation API

### Create Reconciliation Run

**Request**
```
POST /api/reconciliation/runs
Content-Type: application/json
Authorization: Bearer <token>

{
  "settlement_period": "2026-05-01",
  "amount_tolerance": 0.01,
  "date_tolerance_days": 1,
  "notes": "May reconciliation"
}
```

**Response** (201 Created)
```json
{
  "id": "RECON-a1b2c3d4e5f6",
  "status": "PENDING",
  "settlement_period": "2026-05-01",
  "matched_count": 0,
  "unmatched_count": 0,
  "error_count": 0,
  "run_date": "2026-05-01T10:00:00Z",
  "created_at": "2026-05-01T10:00:00Z",
  "updated_at": "2026-05-01T10:00:00Z",
  "created_by": "admin"
}
```

---

### List Reconciliation Runs

**Request**
```
GET /api/reconciliation/runs?skip=0&limit=10&status=PENDING
Authorization: Bearer <token>
```

**Response** (200 OK)
```json
{
  "data": [
    {
      "id": "RECON-a1b2c3d4e5f6",
      "status": "PENDING",
      "settlement_period": "2026-05-01",
      "matched_count": 5000,
      "unmatched_count": 12,
      "run_date": "2026-05-01T10:00:00Z",
      "created_by": "admin"
    }
  ],
  "meta": {
    "total": 1,
    "limit": 10,
    "offset": 0,
    "has_more": false
  }
}
```

---

### Get Reconciliation Run Details

**Request**
```
GET /api/reconciliation/runs/{run_id}
Authorization: Bearer <token>
```

**Response** (200 OK)
```json
{
  "id": "RECON-a1b2c3d4e5f6",
  "status": "IN_PROGRESS",
  "settlement_period": "2026-05-01",
  "matched_count": 5000,
  "unmatched_count": 12,
  "error_count": 0,
  "amount_tolerance": 0.01,
  "date_tolerance_days": 1,
  "run_date": "2026-05-01T10:00:00Z",
  "created_at": "2026-05-01T10:00:00Z",
  "updated_at": "2026-05-01T10:15:00Z",
  "completed_at": null,
  "created_by": "admin"
}
```

---

### Get Unmatched Transactions

**Request**
```
GET /api/reconciliation/runs/{run_id}/unmatches?skip=0&limit=50
Authorization: Bearer <token>
```

**Response** (200 OK)
```json
{
  "data": [
    {
      "id": "UNMATCH-x1y2z3",
      "transaction_id": "TXN-abc123",
      "external_transaction_id": null,
      "amount_difference": 0.50,
      "date_difference_days": 1,
      "reason": "Amount mismatch",
      "resolution_status": "PENDING",
      "resolved_at": null
    }
  ],
  "meta": {
    "total": 12,
    "limit": 50,
    "offset": 0,
    "has_more": false
  }
}
```

---

### Resolve Unmatched Transaction

**Request**
```
PATCH /api/reconciliation/runs/{run_id}/unmatches/{unmatch_id}/resolve
Content-Type: application/json
Authorization: Bearer <token>

{
  "resolution_status": "RESOLVED",
  "comment": "Confirmed with counterparty"
}
```

**Response** (200 OK)
```json
{
  "id": "UNMATCH-x1y2z3",
  "resolution_status": "RESOLVED",
  "resolved_at": "2026-05-01T11:00:00Z",
  "resolved_by": "admin"
}
```

---

### Complete Reconciliation

**Request**
```
POST /api/reconciliation/runs/{run_id}/complete
Authorization: Bearer <token>
```

**Response** (200 OK)
```json
{
  "id": "RECON-a1b2c3d4e5f6",
  "status": "RESOLVED",
  "matched_count": 5000,
  "unmatched_count": 0,
  "completed_at": "2026-05-01T12:00:00Z"
}
```

---

## Transactions API

### Create Transaction

**Request**
```
POST /api/transactions
Content-Type: application/json
Authorization: Bearer <token>

{
  "amount": 150.50,
  "currency": "USD",
  "transaction_type": "DEBIT",
  "external_reference": "TXN-2026-05-001",
  "transaction_date": "2026-05-01T10:30:00Z",
  "description": "Wire transfer",
  "source_system": "jPOS"
}
```

**Response** (201 Created)
```json
{
  "id": "TXN-a1b2c3d4e5f6",
  "amount": 150.50,
  "currency": "USD",
  "transaction_type": "DEBIT",
  "external_reference": "TXN-2026-05-001",
  "status": "NEW",
  "transaction_date": "2026-05-01T10:30:00Z",
  "created_at": "2026-05-01T10:31:00Z",
  "updated_at": "2026-05-01T10:31:00Z"
}
```

---

### List Transactions

**Request**
```
GET /api/transactions?skip=0&limit=100&currency=USD&status=MATCHED&amount[gte]=100&amount[lte]=1000
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip`: Offset (default: 0)
- `limit`: Max results (default: 100)
- `currency`: Filter by currency (e.g., USD, EUR)
- `status`: Filter by status (NEW, MATCHED, UNMATCHED, RESOLVED)
- `transaction_type`: Filter by type (DEBIT, CREDIT)
- `amount[gte]`: Minimum amount
- `amount[lte]`: Maximum amount
- `created_after`: ISO datetime
- `created_before`: ISO datetime
- `order_by`: Sort column (default: -transaction_date)

**Response** (200 OK)
```json
{
  "data": [
    {
      "id": "TXN-a1b2c3d4e5f6",
      "amount": 250.00,
      "currency": "USD",
      "transaction_type": "CREDIT",
      "external_reference": "TXN-2026-05-002",
      "status": "MATCHED",
      "transaction_date": "2026-05-01T10:30:00Z",
      "created_at": "2026-05-01T10:31:00Z"
    }
  ],
  "meta": {
    "total": 5000,
    "limit": 100,
    "offset": 0,
    "has_more": true
  }
}
```

---

### Get Transaction Details

**Request**
```
GET /api/transactions/{transaction_id}
Authorization: Bearer <token>
```

**Response** (200 OK)
```json
{
  "id": "TXN-a1b2c3d4e5f6",
  "amount": 150.50,
  "currency": "USD",
  "transaction_type": "DEBIT",
  "external_reference": "TXN-2026-05-001",
  "status": "MATCHED",
  "transaction_date": "2026-05-01T10:30:00Z",
  "description": "Wire transfer",
  "source_system": "jPOS",
  "created_at": "2026-05-01T10:31:00Z",
  "updated_at": "2026-05-01T10:35:00Z",
  "reconciliation_run_id": "RECON-a1b2c3d4e5f6",
  "settlement_batch_id": "BATCH-a1b2c3d4e5f6"
}
```

---

### Bulk Import Transactions

**Request**
```
POST /api/transactions/bulk-import
Content-Type: application/json
Authorization: Bearer <token>

{
  "source_system": "jPOS",
  "transactions": [
    {
      "amount": 100.00,
      "currency": "USD",
      "transaction_type": "DEBIT",
      "external_reference": "TXN-001",
      "transaction_date": "2026-05-01T10:00:00Z"
    },
    {
      "amount": 200.00,
      "currency": "USD",
      "transaction_type": "CREDIT",
      "external_reference": "TXN-002",
      "transaction_date": "2026-05-01T10:05:00Z"
    }
  ]
}
```

**Response** (201 Created)
```json
{
  "imported_count": 2,
  "failed_count": 0,
  "message": "2 transactions imported successfully"
}
```

---

### Search Transactions

**Request**
```
GET /api/transactions/search?q=TXN-2026&skip=0&limit=20
Authorization: Bearer <token>
```

**Response** (200 OK)
```json
{
  "data": [
    {
      "id": "TXN-a1b2c3d4e5f6",
      "amount": 150.50,
      "external_reference": "TXN-2026-05-001",
      "status": "MATCHED",
      "created_at": "2026-05-01T10:31:00Z"
    }
  ],
  "meta": {
    "total": 3,
    "limit": 20,
    "offset": 0,
    "has_more": false
  }
}
```

---

## Fraud API

### Create Fraud Rule

**Request**
```
POST /api/fraud/rules
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "High Amount Debit",
  "description": "Alert on large debit transactions",
  "condition": "amount > 100000 AND transaction_type == 'DEBIT'",
  "weight": 30,
  "enabled": true,
  "priority": 1
}
```

**Response** (201 Created)
```json
{
  "id": "RULE-a1b2c3d4e5f6",
  "name": "High Amount Debit",
  "condition": "amount > 100000 AND transaction_type == 'DEBIT'",
  "weight": 30,
  "enabled": true,
  "priority": 1,
  "created_at": "2026-05-01T10:00:00Z"
}
```

---

### List Fraud Rules

**Request**
```
GET /api/fraud/rules?enabled=true&skip=0&limit=50
Authorization: Bearer <token>
```

**Response** (200 OK)
```json
{
  "data": [
    {
      "id": "RULE-a1b2c3d4e5f6",
      "name": "High Amount Debit",
      "weight": 30,
      "enabled": true,
      "priority": 1,
      "created_at": "2026-05-01T10:00:00Z"
    }
  ],
  "meta": {
    "total": 5,
    "limit": 50,
    "offset": 0,
    "has_more": false
  }
}
```

---

### List Fraud Alerts

**Request**
```
GET /api/fraud/alerts?skip=0&limit=50&status=PENDING&risk_level=HIGH
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip`: Offset (default: 0)
- `limit`: Max results (default: 50)
- `status`: Filter by status (PENDING, REVIEWED, APPROVED, REJECTED)
- `risk_level`: Filter by risk (LOW, MEDIUM, HIGH)
- `order_by`: Sort by (default: -alert_date)

**Response** (200 OK)
```json
{
  "data": [
    {
      "id": "ALERT-a1b2c3d4e5f6",
      "transaction_id": "TXN-abc123",
      "risk_score": 75.5,
      "risk_level": "HIGH",
      "status": "PENDING",
      "alert_date": "2026-05-01T10:35:00Z",
      "triggered_rules": ["RULE-1", "RULE-3"]
    }
  ],
  "meta": {
    "total": 8,
    "limit": 50,
    "offset": 0,
    "has_more": false
  }
}
```

---

### Review Fraud Alert

**Request**
```
PATCH /api/fraud/alerts/{alert_id}/review
Content-Type: application/json
Authorization: Bearer <token>

{
  "decision": "APPROVED",
  "comment": "Legitimate transaction, known customer"
}
```

**Response** (200 OK)
```json
{
  "id": "ALERT-a1b2c3d4e5f6",
  "status": "APPROVED",
  "reviewed_at": "2026-05-01T11:00:00Z",
  "reviewed_by": "admin",
  "resolution_comment": "Legitimate transaction, known customer"
}
```

---

### Get Fraud Summary

**Request**
```
GET /api/fraud/summary
Authorization: Bearer <token>
```

**Response** (200 OK)
```json
{
  "total_alerts": 125,
  "pending_alerts": 8,
  "high_risk_count": 3,
  "medium_risk_count": 5,
  "low_risk_count": 117,
  "average_risk_score": 28.5
}
```

---

## Settlement API

### Create Settlement Batch

**Request**
```
POST /api/settlement/batches
Content-Type: application/json
Authorization: Bearer <token>

{
  "settlement_period": "2026-05-01",
  "currency": "USD",
  "notes": "Daily USD settlement"
}
```

**Response** (201 Created)
```json
{
  "id": "BATCH-a1b2c3d4e5f6",
  "settlement_period": "2026-05-01",
  "currency": "USD",
  "status": "DRAFT",
  "batch_date": "2026-05-01T10:00:00Z",
  "total_amount": 0,
  "transaction_count": 0,
  "created_at": "2026-05-01T10:00:00Z"
}
```

---

### Add Transactions to Batch

**Request**
```
POST /api/settlement/batches/{batch_id}/transactions
Content-Type: application/json
Authorization: Bearer <token>

{
  "transaction_ids": ["TXN-001", "TXN-002", "TXN-003"]
}
```

**Response** (200 OK)
```json
{
  "id": "BATCH-a1b2c3d4e5f6",
  "total_amount": 5000.00,
  "transaction_count": 3,
  "debit_amount": 3000.00,
  "credit_amount": 2000.00,
  "net_amount": 1000.00,
  "net_direction": "DEBIT"
}
```

---

### Finalize Settlement Batch

**Request**
```
POST /api/settlement/batches/{batch_id}/finalize
Content-Type: application/json
Authorization: Bearer <token>

{
  "reference": "SETL-2026-05-001"
}
```

**Response** (200 OK)
```json
{
  "id": "BATCH-a1b2c3d4e5f6",
  "status": "FINALIZED",
  "reference": "SETL-2026-05-001",
  "finalized_at": "2026-05-01T16:00:00Z",
  "net_amount": 1000.00,
  "net_direction": "DEBIT"
}
```

---

### Create Settlement Statement

**Request**
```
POST /api/settlement/statements
Content-Type: application/json
Authorization: Bearer <token>

{
  "settlement_period": "2026-05-01"
}
```

**Response** (201 Created)
```json
{
  "id": "STMT-a1b2c3d4e5f6",
  "settlement_period": "2026-05-01",
  "status": "DRAFT",
  "statement_date": "2026-05-01T10:00:00Z",
  "total_transactions": 5000,
  "total_amount": 500000.00,
  "total_debit_amount": 300000.00,
  "total_credit_amount": 200000.00,
  "net_settlement": 100000.00,
  "prepared_by": "admin"
}
```

---

### Get Daily NET Settlement

**Request**
```
GET /api/settlement/daily-summary?date=2026-05-01
Authorization: Bearer <token>
```

**Response** (200 OK)
```json
{
  "data": [
    {
      "currency": "USD",
      "debit_total": 500000.00,
      "credit_total": 400000.00,
      "net_amount": 100000.00,
      "net_direction": "DEBIT",
      "batch_count": 5
    },
    {
      "currency": "EUR",
      "debit_total": 200000.00,
      "credit_total": 210000.00,
      "net_amount": 10000.00,
      "net_direction": "CREDIT",
      "batch_count": 2
    }
  ]
}
```

---

## Reporting API

### Create Report Job

**Request**
```
POST /api/reports/generate
Content-Type: application/json
Authorization: Bearer <token>

{
  "report_type": "reconciliation",
  "format": "PDF",
  "settlement_period": "2026-05-01"
}
```

**Response** (202 Accepted)
```json
{
  "id": "JOB-a1b2c3d4e5f6",
  "report_type": "reconciliation",
  "format": "PDF",
  "status": "PENDING",
  "created_at": "2026-05-01T10:00:00Z",
  "requested_by": "admin"
}
```

---

### Get Report Job Status

**Request**
```
GET /api/reports/jobs/{job_id}
Authorization: Bearer <token>
```

**Response** (200 OK)
```json
{
  "id": "JOB-a1b2c3d4e5f6",
  "report_type": "reconciliation",
  "format": "PDF",
  "status": "COMPLETED",
  "file_path": "/reports/report_reconciliation_2026-05-01.pdf",
  "file_size_bytes": 125000,
  "created_at": "2026-05-01T10:00:00Z",
  "completed_at": "2026-05-01T10:15:00Z",
  "expires_at": "2026-05-31T10:00:00Z"
}
```

---

### Download Report

**Request**
```
GET /api/reports/jobs/{job_id}/download
Authorization: Bearer <token>
```

**Response** (200 OK with file attachment)

---

## Dashboard API

### Get Dashboard Summary

**Request**
```
GET /api/dashboard/summary
Authorization: Bearer <token>
```

**Response** (200 OK)
```json
{
  "total_transactions_today": 5000,
  "total_amount_today": 500000.00,
  "pending_reconciliation_runs": 1,
  "matched_percentage": 99.76,
  "fraud_alerts_pending": 3,
  "high_risk_alerts": 1,
  "pending_settlements": 2,
  "net_settlement_amount": 50000.00,
  "last_update": "2026-05-01T11:30:00Z"
}
```

---

## NET Settlement API

### Get Settlement Positions

**Request**
```
GET /api/net-settlement/positions?date=2026-05-01
Authorization: Bearer <token>
```

**Response** (200 OK)
```json
{
  "settlement_date": "2026-05-01",
  "positions": [
    {
      "currency": "USD",
      "debit_total": 500000.00,
      "credit_total": 400000.00,
      "net_amount": 100000.00,
      "net_direction": "DEBIT"
    },
    {
      "currency": "EUR",
      "debit_total": 200000.00,
      "credit_total": 210000.00,
      "net_amount": 10000.00,
      "net_direction": "CREDIT"
    }
  ]
}
```

---

## Error Response Format

All errors follow consistent format:

```json
{
  "detail": "Description of error",
  "status": 400,
  "timestamp": "2026-05-01T10:00:00Z"
}
```

Common HTTP Status Codes:
- `200`: Success
- `201`: Created
- `202`: Accepted (async)
- `400`: Bad Request (validation error)
- `401`: Unauthorized (missing/invalid token)
- `404`: Not Found
- `500`: Server Error

---

## Implementation Notes for Phase 3

1. **Route Structure**: Create file per router (reconciliation.py, transactions.py, etc.)
2. **Dependency Injection**: Use FastAPI `Depends()` for:
   - `require_jwt_token` (auth)
   - `get_db` (database session)
3. **Error Handling**: Use `HTTPException` with appropriate status codes
4. **Validation**: Use Pydantic schemas for request/response validation
5. **Pagination**: Implement skip/limit pattern with `has_more` flag
6. **Status Codes**: Use 201 for creation, 202 for async, 200 for success
7. **Async**: Use `async def` for all endpoints
8. **Docstrings**: Document each endpoint with description and examples
