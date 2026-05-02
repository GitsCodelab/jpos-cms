# Phase 2 - Main Menu & Credit Management System

**Status**: 🟡 **Planned** (Design complete, implementation pending)  
**Updated**: May 2, 2026

## Overview

Phase 2 builds the core business functionality for the jpos-cms CMS. It implements a main navigation menu and credit management system, building on Phase 1's authentication foundation.

**Depends on**: Phase 1 (authentication) must be complete first.

---

## Goal

Implement the main application menu and credit/debit card management system for the jpos-cms financial institution CMS.

This phase focuses on:
- Main navigation menu
- GL (General Ledger) accounts management
- Card management (Credit, Debit, Prepaid)
- Card holders (Customer/Individual)
- Account settings
- Balance type configuration

---

## Architecture Notes

**Design Phase Complete**:
- Backend: 12 ORM models designed for fintech domain (in backend/app/models.py)
- Services: 5 domain services with business logic (reconciliation, transaction, fraud, settlement, reporting)
- Repository: Generic CRUD pattern implemented for all models
- API: 40+ endpoints designed in backend/API_SPECIFICATION.md

**Technology Stack** (builds on Phase 1):
- Backend: FastAPI with service/repository pattern
- Frontend: React with protected routes from Phase 1
- Database: SQLAlchemy ORM (PostgreSQL/Oracle compatible)
- Authentication: JWT from Phase 1 (will extend with RBAC)

---

## Features (Planned)

### UI Components
- Main sidebar navigation menu
- Dashboard with financial metrics
- CRUD interfaces for each entity type
- Search and filter capabilities
- Bulk operations support
- Responsive design (desktop-first)

### Entities
- **GL Accounts**: Chart of accounts, account types, hierarchies
- **Cards**: Issue, manage, track card products
- **Card Holders**: Customer/individual linked to cards
- **Customers**: Customer master data
- **Settings**: Balance types, configurations, policies

### Core Functionality
- Create/Read/Update/Delete for all entities
- Relationship management (card holder → cards → accounts)
- Validation rules and constraints
- Audit trail for all changes
- Bulk import/export capabilities
- Advanced filtering and search

---

## Backend Implementation Plan

### Models (Already Designed - See backend/app/models.py)
```python
# Already in models.py (400+ lines):
- Transaction (high-volume, ~1M/month)
- ReconciliationRun, ReconciliationUnmatch
- FraudRule, FraudAlert
- SettlementBatch, SettlementStatement
- ReportJob
- (and more...)

# Phase 2 needs to add:
- GLAccount
- Card, CardProduct
- CardHolder
- Customer
- BalanceType
- (domain-specific models)
```

### Services (Architecture Ready)
```
services/
├── gl_account_service.py       # GL account CRUD + validation
├── card_service.py             # Card management + lifecycle
├── cardholder_service.py        # Cardholder CRUD
├── customer_service.py          # Customer master data
├── settings_service.py          # Configuration management
└── (already implemented)
    ├── reconciliation_service.py
    ├── transaction_service.py
    ├── fraud_service.py
    ├── settlement_service.py
    └── reporting_service.py
```

### Routers (API Endpoints)
```
routers/
├── gl_accounts.py    # REST endpoints for GL accounts
├── cards.py          # REST endpoints for cards
├── cardholders.py    # REST endpoints for cardholders
├── customers.py      # REST endpoints for customers
├── settings.py       # REST endpoints for settings
└── (already implemented)
    ├── auth.py
    ├── transactions.py
    ├── reconciliation.py
    ├── fraud.py
    ├── settlement.py
    └── dashboard.py
```

### API Endpoints (TBD - See backend/API_SPECIFICATION.md)
```
GL Accounts:
  GET    /api/gl-accounts           # List all
  POST   /api/gl-accounts           # Create
  GET    /api/gl-accounts/{id}      # Get one
  PATCH  /api/gl-accounts/{id}      # Update
  DELETE /api/gl-accounts/{id}      # Delete

Cards:
  GET    /api/cards                 # List
  POST   /api/cards                 # Create
  GET    /api/cards/{id}            # Get
  PATCH  /api/cards/{id}            # Update
  DELETE /api/cards/{id}            # Delete

(Similar for cardholders, customers, settings...)
```

---

## Frontend Implementation Plan

### Pages (Already Scaffolded)
```jsx
pages/
├── Dashboard.jsx              # Main dashboard (exists but empty)
├── GLAccounts.jsx            # GL account list/detail
├── Cards.jsx                 # Card management
├── CardHolders.jsx           # Cardholder management
├── Customers.jsx             # Customer list
├── Settings.jsx              # Settings page
├── Transactions.jsx          # Transaction list (exists)
├── Reconciliation.jsx        # Reconciliation (exists)
├── Fraud.jsx                 # Fraud alerts (exists)
├── Settlement.jsx            # Settlement (exists)
└── NetSettlement.jsx         # NET settlement (exists)
```

### Components
```jsx
components/
├── DataTable.jsx             # Reusable table component
├── SearchFilter.jsx          # Search/filter form
├── EntityForm.jsx            # Generic CRUD form
├── BulkActions.jsx           # Bulk operations
└── (others as needed)
```

### Navigation
```jsx
// Main menu structure
Menu Items:
- Dashboard
- Credit Management
  - GL Accounts
  - Cards
  - Card Holders
  - Customers
- Settings
  - Balance Types
  - Configurations
- Monitoring (Phase 3)
  - Transactions
  - Reconciliation
  - Fraud Alerts
  - Settlement
- Reporting (Phase 3)
```

---

## Database Schema

### Phase 2 Models to Add

```sql
-- GL Accounts
CREATE TABLE gl_accounts (
  id VARCHAR(50) PRIMARY KEY,
  account_code VARCHAR(50) UNIQUE NOT NULL,
  account_name VARCHAR(200) NOT NULL,
  account_type VARCHAR(50),  -- Asset, Liability, Equity, Revenue, Expense
  currency VARCHAR(3),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Card Products
CREATE TABLE card_products (
  id VARCHAR(50) PRIMARY KEY,
  product_name VARCHAR(200) NOT NULL,
  card_type VARCHAR(50),  -- Credit, Debit, Prepaid
  issuer_id VARCHAR(50),
  created_at TIMESTAMP
);

-- Cards
CREATE TABLE cards (
  id VARCHAR(50) PRIMARY KEY,
  card_number VARCHAR(16) NOT NULL,
  product_id VARCHAR(50) FOREIGN KEY,
  cardholder_id VARCHAR(50) FOREIGN KEY,
  status VARCHAR(50),  -- Active, Blocked, Expired
  issue_date DATE,
  expiry_date DATE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Card Holders
CREATE TABLE cardholders (
  id VARCHAR(50) PRIMARY KEY,
  customer_id VARCHAR(50) FOREIGN KEY,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  email VARCHAR(150),
  phone VARCHAR(20),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Customers
CREATE TABLE customers (
  id VARCHAR(50) PRIMARY KEY,
  customer_name VARCHAR(200) NOT NULL,
  customer_type VARCHAR(50),  -- Individual, Corporate
  email VARCHAR(150),
  phone VARCHAR(20),
  address VARCHAR(500),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Balance Types
CREATE TABLE balance_types (
  id VARCHAR(50) PRIMARY KEY,
  type_name VARCHAR(100) NOT NULL,
  description VARCHAR(500),
  created_at TIMESTAMP
);
```

---

## API Specification

See `backend/API_SPECIFICATION.md` for full details of 40+ endpoints.

**Example GET endpoint**:
```
GET /api/gl-accounts?page=1&limit=20&sort=account_code&filter=is_active:true

Response 200:
{
  "items": [
    {
      "id": "ACC001",
      "account_code": "1000",
      "account_name": "Cash",
      "account_type": "Asset",
      "currency": "USD",
      "is_active": true,
      "created_at": "2026-05-01T10:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20
}
```

---

## Testing Plan

### Unit Tests
- Service methods (validation, business logic)
- Model constraints
- Error handling

### Integration Tests
- API endpoints (CRUD operations)
- Relationships between entities
- Data validation
- Authorization checks

### UI Tests
- Form submission
- Pagination
- Filtering/searching
- Bulk operations

---

## Security Requirements

### Build on Phase 1:
- JWT authentication ✓
- Protected endpoints ✓
- CORS middleware ✓

### Phase 2 Additions:
- RBAC (Role-Based Access Control) - coming later
  - Admin can manage everything
  - Managers can view/edit GL accounts
  - Operators can view reports
- Audit logging for all changes
- Data encryption at rest
- Field-level masking (card numbers, SSN)

---

## Performance Considerations

- **Database indexes** on frequently queried columns (account_code, customer_id, card_number)
- **Pagination** for large result sets (GL accounts, cards, transactions)
- **Caching** for master data (card products, balance types)
- **Batch operations** for bulk import/export
- **Query optimization** for relationship traversal

---

## Known Constraints

1. **Card numbers**: Must be encrypted in database, never logged
2. **Customer data**: Subject to KYC/AML regulations
3. **Audit trail**: Immutable, retention policy (7 years)
4. **Relationships**: Cascading deletes must maintain data integrity
5. **Concurrency**: Optimistic locking for GL accounts (prevent double-posting)

---

## Deliverables

- [ ] All models in models.py with relationships
- [ ] Service layer for each entity type
- [ ] REST API endpoints (CRUD for each entity)
- [ ] Frontend pages with data tables
- [ ] Navigation menu integrated
- [ ] Database migrations
- [ ] Integration tests
- [ ] API documentation
- [ ] User guide

---

## Success Criteria

- [ ] Can create/read/update/delete all entities
- [ ] Relationships properly enforced (cardholder → cards → accounts)
- [ ] Search and filtering work
- [ ] Pagination works for large datasets
- [ ] Bulk operations complete
- [ ] Audit trail tracks all changes
- [ ] Tests coverage > 80%
- [ ] Performance acceptable (<200ms per request)

---

## Timeline Estimate

**Effort**: 60-80 hours
- Backend services/APIs: 30-40 hours
- Frontend pages/components: 20-30 hours
- Testing: 10-15 hours
- Documentation: 5 hours

**Depends on**:
- Phase 1 complete and security-hardened
- Design review and approval

---

## References

- **Design**: backend/FINTECH_CMS_ARCHITECTURE.md
- **API Spec**: backend/API_SPECIFICATION.md
- **Models**: backend/app/models.py (400+ lines)
- **Services**: backend/app/services/ (1000+ lines)
- **Repository Pattern**: backend/app/repositories/base_repository.py

---

## Notes

**This document replaces the placeholder init-main-menu.md**

Original file had duplicate Phase 1 requirements (copy-pasted). This corrected version:
- Documents Phase 2 properly
- References existing design (models, services, repositories)
- Provides clear API design
- Includes database schema
- Estimates effort and timeline

**Next Step**: After Phase 1 is complete and hardened, start Phase 2 design review and planning.
* proper validation and sanitization
* proper error responses
* token expiration validation

---

# Database Requirements

* Oracle-ready structure
* database abstraction support
* scalable user model
* future role support
* future audit logging support

---

# Frontend UX Requirements

* modern login page
* responsive design
* loading states
* error messages
* invalid credential handling
* logout redirect
* session expiration redirect

---

# Technical Requirements

* scalable architecture
* production ready
* Docker compatible
* modular structure
* service/repository separation
* maintainable code structure
* async-ready architecture

---

# Implementation Rules

* avoid breaking existing endpoints
* keep modular architecture
* maintain Docker compatibility
* explain created files before implementation
* follow existing project structure
* avoid duplicated logic
* use reusable services/components

---

# Acceptance Criteria

* user can login successfully
* invalid login shows proper error
* JWT token is generated correctly
* token persists after page refresh
* protected pages require authentication
* logout clears session correctly
* protected backend endpoints reject invalid tokens
* frontend redirects unauthenticated users properly
* authentication flow works inside Docker environment

---

# Review & Testing

Tasks:

* test backend login flow
* test frontend login flow
* test protected APIs
* test token persistence
* test logout flow
* test invalid credentials
* test unauthorized access handling
* solve any issue discovered during testing

---

# Github Workflow

* create clean commits
* explain major changes before commit
* do NOT push automatically
* keep commits modular and readable

---

# Non Goals

This phase does NOT include:

* OAuth
* MFA
* RBAC
* permissions management
* SSO integration
* audit trail implementation
* advanced fraud detection
