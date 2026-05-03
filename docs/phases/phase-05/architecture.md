# Phase 05 — Customer Management Architecture

## Goal

Implement read-only customer search and detail views for the fintech CMS platform. All customer
data is read from the **external business database** (Oracle or PostgreSQL) configured via the
CMS Database Connections table — never from the CMS internal PostgreSQL.

---

## Design Principles

- **Read-only access** — no create/update/delete endpoints. Customer data is owned by the jPOS switch.
- **Dynamic DB connection** — the active `DatabaseConnection` record drives which external DB is queried.
- **Oracle-first SQL** — no PostgreSQL-specific syntax in repositories or queries.
- **PAN masking at service layer** — full card numbers from the DB are never returned to callers.
- **Role-based field restriction** — account balance is `null` for `viewer` role.
- **Minimum search input** — empty input and input shorter than 3 chars are rejected with HTTP 400.
- **Separate ORM metadata** — business models use `BusinessBase` (separate `MetaData`), keeping Alembic migrations isolated from external DB tables.
- **Engine caching** — a SQLAlchemy engine is built once per active connection and reused across requests.

---

## Architecture Layers

```
Router (customer.py)
  └── Service (customer_service.py)
        └── db_business.get_business_db(cms_db)
              └── db_connection_repository.get_active(cms_db)    ← CMS DB
              └── get_business_engine(connection)                 ← External DB engine cache
        └── Repository (customer_repository.py, …)               ← External DB queries
```

---

## Backend Files

### New Files

| File | Purpose |
|---|---|
| `app/db_business.py` | Dynamic engine + session factory for external DB |
| `app/models_business.py` | SQLAlchemy ORM models for external DB (BusinessBase) |
| `app/repositories/customer_repository.py` | Customer search + lookup |
| `app/repositories/customer_contract_repository.py` | Contract list by customer |
| `app/repositories/customer_card_repository.py` | Card list by customer |
| `app/repositories/customer_account_repository.py` | Account list by customer |
| `app/repositories/customer_document_repository.py` | Document list by customer |
| `app/repositories/customer_contact_repository.py` | Contact list by customer |
| `app/services/customer_service.py` | Business logic: search, masking, access control |
| `app/routers/customer.py` | 7 REST endpoints under `/customers` |

### Modified Files

| File | Change |
|---|---|
| `app/main.py` | Import and register `customer_router` |
| `app/schemas.py` | Added 8 customer Pydantic response schemas |

---

## API Endpoints

All endpoints require a valid JWT Bearer token.

| Method | Path | Description | Role Restriction |
|---|---|---|---|
| GET | `/customers` | Paginated customer search | All authenticated |
| GET | `/customers/{id}` | Customer detail | All authenticated |
| GET | `/customers/{id}/contracts` | Contract list | All authenticated |
| GET | `/customers/{id}/cards` | Card list (PAN masked) | All authenticated |
| GET | `/customers/{id}/accounts` | Account list (balance restricted for viewer) | viewer: balance=null |
| GET | `/customers/{id}/documents` | KYC document list | All authenticated |
| GET | `/customers/{id}/contacts` | Contact list | All authenticated |

### Search Query Parameters (`GET /customers`)

| Param | Required | Notes |
|---|---|---|
| `q` | One of q/national_id required | Prefix search: name, mobile, email, national_id |
| `national_id` | One of q/national_id required | Exact match |
| `status` | No | Filter: ACTIVE, INACTIVE, BLOCKED, SUSPENDED |
| `segment` | No | Filter: RETAIL, CORPORATE, VIP, SME |
| `page` | No | Default 1, max 200 |
| `page_size` | No | Default 25, max 100 |

---

## Business Models (`models_business.py`)

All models declare `__table_args__ = {"schema": _SCHEMA}` when `BUSINESS_SCHEMA` env var is set.
This supports Oracle schemas (e.g. `MAIN.customers`).

| Model | Table | Key Fields |
|---|---|---|
| `Customer` | `customers` | id, first_name, last_name, national_id, mobile, email, status, segment |
| `CustomerContract` | `customer_contracts` | id, customer_id, contract_number, product_type, status |
| `CustomerCard` | `customer_cards` | id, customer_id, card_number (masked at service), card_type, status |
| `CustomerAccount` | `customer_accounts` | id, customer_id, account_number, currency, balance, status |
| `CustomerDocument` | `customer_documents` | id, customer_id, document_type, document_number |
| `CustomerContact` | `customer_contacts` | id, customer_id, contact_type, contact_value, is_primary |

---

## Dynamic DB Connection (`db_business.py`)

1. `get_business_db(cms_db)` resolves the active `DatabaseConnection` from CMS DB.
2. Builds a SQLAlchemy engine URL for Oracle (`oracle+cx_oracle://`) or PostgreSQL (`postgresql+psycopg2://`).
3. Engine is cached in `_engine_cache[connection.id]` to avoid reconnecting on every request.
4. Call `invalidate_engine(connection_id)` when a connection is deactivated or its credentials are updated.
5. Session is caller-managed — caller must call `session.close()`.

---

## Security

- **PAN masking** — `_mask_card()` in `customer_service.py` returns `****-****-****-XXXX` format.
- **Balance restriction** — `include_balance` is `False` for `role == "viewer"`, returning `null` in API response.
- **Input validation** — search rejects empty/short inputs with HTTP 400 before touching the DB.
- **No customer write endpoints** — module is entirely read-only by design.
- **JWT required** — all endpoints depend on `require_jwt_token`.

---

## Frontend Files

| File | Purpose |
|---|---|
| `src/services/customerApi.js` | 7 Axios API methods |
| `src/pages/Customers.jsx` | Search page: bar, filters, results table, pagination |
| `src/pages/CustomerDetail.jsx` | Detail page: header, descriptions, 5-tab layout |
| `src/components/customer/tabs/ContractsTab.jsx` | Contracts table (lazy-loaded) |
| `src/components/customer/tabs/CardsTab.jsx` | Cards table (masked PAN) |
| `src/components/customer/tabs/AccountsTab.jsx` | Accounts table (balance nullable) |
| `src/components/customer/tabs/DocumentsTab.jsx` | Documents table |
| `src/components/customer/tabs/ContactsTab.jsx` | Contacts table |

### Routes Added to `App.jsx`

```
/customers         → Customers.jsx
/customers/:id     → CustomerDetail.jsx
```

---

## Menu Integration

The `/customers` path is already present in the `issuing` group of `menu_seed.py` under:

```
issuing → Customers (/customers) — permission: customers.list
```

No additional seed changes are required. The Standard profile includes it automatically.

---

## Oracle Compatibility Notes

- All queries use `func.upper()` for case-insensitive string matching (no `ILIKE`).
- `nullslast()` used for nullable date ordering in contract repository.
- No CTEs, window functions, or PostgreSQL-specific types in repository queries.
- Schema prefix controlled by `BUSINESS_SCHEMA` env var for Oracle schema isolation.
- Set `BUSINESS_SCHEMA=MAIN` in `docker-compose.yml` env for Oracle deployments.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `BUSINESS_SCHEMA` | _(empty)_ | Oracle schema prefix (e.g. `MAIN`) |

---

## Deployment Notes

After implementing Phase 05:

1. Rebuild Docker images: `docker compose up --build -d`
2. No database migrations needed for CMS DB (no new CMS tables).
3. Confirm external DB table names match `models_business.py` with DBA.
4. Set `BUSINESS_SCHEMA` if Oracle schema prefix is required.
5. Activate the correct `DatabaseConnection` in Configuration → Database Connections.

