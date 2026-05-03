# Phase 05 - Tasks - Customer Management

## Goal

Implement scalable customer search and customer details modules for the fintech CMS platform.

Supported operations:
* customer search (by name, national ID, card number, account number, mobile, email)
* customer detail header
* linked contracts
* linked cards
* linked accounts
* linked documents
* linked contacts

---

## Critical Architecture Note — Business DB Connection

> **The customer module is a business API.**
> It does NOT read from the CMS internal PostgreSQL database (`jpos_cms.db` / `cms_user`).
> It reads from the **external Oracle/PostgreSQL business database** configured in the DB Connections table.

### How It Works

1. On every business API request the service resolves the active connection via:
   ```python
   db_connection_repository.get_active(cms_db)
   ```
2. It decrypts the stored credentials using `decrypt_password()` from `db_connection_service.py`.
3. It opens a **dynamic SQLAlchemy session** to the external database for that request.
4. If no active connection exists → return `503 Service Unavailable` immediately.

### Rule

- All `GET /customers/*` endpoints accept the CMS `db: Session` (PostgreSQL) **only** to resolve the active connection.
- A second `business_db: Session` is opened dynamically per request against the external target DB.
- Never hardcode a second database URL. Always read it from the active `DatabaseConnection` record.

---

# Backend Tasks

## 1. Dynamic Business Session Utility

* [x] create `backend/app/db_business.py`
  * `get_business_engine(connection: DatabaseConnection) -> Engine`
    * builds SQLAlchemy URL from decrypted host/port/service/user/pass
    * supports `oracle+cx_oracle://` and `postgresql+psycopg2://` based on `database_type`
  * `get_business_session(cms_db: Session) -> Generator[Session, None, None]`
    * resolves active connection via `db_connection_repository.get_active(cms_db)`
    * raises `HTTPException 503` if no active connection
    * yields a scoped session to the external DB
    * closes session on exit

Requirements:
* reusable across all business API modules (customer, transactions, etc.)
* connection engine should be cached by connection ID to avoid reconnecting on every request
* engine cache must be invalidated when a connection is deactivated or updated

---

## 2. Customer Models (External DB Mirror)

* [x] create `backend/app/models_business.py`
  * `Customer` — id, first_name, last_name, national_id, mobile, email, status, segment, branch_id, created_at
  * `CustomerContract` — id, customer_id, contract_number, product_type, status, open_date, close_date
  * `CustomerCard` — id, customer_id, card_number (masked), card_type, status, expiry_date
  * `CustomerAccount` — id, customer_id, account_number, currency, balance, status
  * `CustomerDocument` — id, customer_id, document_type, document_number, issue_date, expiry_date
  * `CustomerContact` — id, customer_id, contact_type, contact_value, is_primary

Requirements:
* these models map to **read-only views/tables on the external Oracle DB**
* use `__table_args__ = {'schema': ...}` if Oracle schema name is required
* all models must be declared against a separate `MetaData()` object (not the CMS `Base`)
* column names must match external DB exactly — confirm with DBA before implementing

---

## 3. Customer Schemas

* [x] `CustomerSearchResult` — id, full_name, national_id, mobile, email, status, segment
* [x] `CustomerSearchResponse` — items: List[CustomerSearchResult], total, page, page_size, pages
* [x] `CustomerDetailResponse` — all customer header fields
* [x] `CustomerContractResponse` — contract fields
* [x] `CustomerCardResponse` — card fields (card number masked: show last 4 only)
* [x] `CustomerAccountResponse` — account fields (balance included only for authorized roles)
* [x] `CustomerDocumentResponse` — document fields
* [x] `CustomerContactResponse` — contact fields

Requirements:
* card number must never be returned in full — mask as `****-****-****-1234`
* balance exposure must check JWT role (`admin` or `operator` only)

---

## 4. Customer Repository

* [x] create `backend/app/repositories/customer_repository.py`
  * `search(business_db, q, card_number, account_number, national_id, status, segment, page, page_size)`
    * use two-phase search: resolve IDs first, then fetch full rows by PK
    * use `FETCH FIRST n ROWS ONLY` (Oracle) or `LIMIT/OFFSET` (PostgreSQL) based on dialect
    * compute `COUNT(*)` only on page 1; return `None` on subsequent pages
    * require minimum 3 characters in any search input — raise `ValueError` if below threshold
    * never return results for empty / no-input queries
  * `get_by_id(business_db, customer_id)`

* [x] create `backend/app/repositories/customer_contract_repository.py`
  * `get_by_customer(business_db, customer_id)`

* [x] create `backend/app/repositories/customer_card_repository.py`
  * `get_by_customer(business_db, customer_id)`

* [x] create `backend/app/repositories/customer_account_repository.py`
  * `get_by_customer(business_db, customer_id)`

* [x] create `backend/app/repositories/customer_document_repository.py`
  * `get_by_customer(business_db, customer_id)`

* [x] create `backend/app/repositories/customer_contact_repository.py`
  * `get_by_customer(business_db, customer_id)`

Requirements:
* all repositories accept `business_db: Session` — never import `get_db` from `app.db`
* keep Oracle-compatible SQL (no PostgreSQL-specific functions)
* use function-based index patterns for name searches: `func.upper(Customer.last_name)`

---

## 5. Customer Service

* [x] create `backend/app/services/customer_service.py`
  * `search(cms_db, params) -> CustomerSearchResponse`
    * resolves active connection
    * opens business session
    * delegates to `customer_repository.search()`
  * `get_detail(cms_db, customer_id) -> CustomerDetailResponse`
  * `get_contracts(cms_db, customer_id) -> List[CustomerContractResponse]`
  * `get_cards(cms_db, customer_id) -> List[CustomerCardResponse]`
  * `get_accounts(cms_db, customer_id, token_role) -> List[CustomerAccountResponse]`
  * `get_documents(cms_db, customer_id) -> List[CustomerDocumentResponse]`
  * `get_contacts(cms_db, customer_id) -> List[CustomerContactResponse]`

Requirements:
* card masking applied at service layer before returning schema
* balance returned conditionally based on `token_role`
* 503 propagated if no active connection

---

## 6. Customer Router

* [x] create `backend/app/routers/customer.py`
* [x] register router in `backend/app/main.py`

Endpoints:

| Method | Path | Description |
|---|---|---|
| `GET` | `/customers` | Search customers (requires `q` or `card_number` or `account_number`) |
| `GET` | `/customers/{id}` | Customer detail header |
| `GET` | `/customers/{id}/contracts` | Linked contracts |
| `GET` | `/customers/{id}/cards` | Linked cards (masked) |
| `GET` | `/customers/{id}/accounts` | Linked accounts |
| `GET` | `/customers/{id}/documents` | Linked documents |
| `GET` | `/customers/{id}/contacts` | Linked contacts |

Requirements:
* all endpoints require `require_jwt_token`
* `GET /customers` must reject empty query with `400 Bad Request`
* `GET /customers/{id}/accounts` must reject `viewer` role with `403 Forbidden`
* return `503` with a clear message if no active DB connection is configured

---

# Frontend Tasks

## 7. Customer API Service

* [x] create `frontend/src/services/customerApi.js`
  * `searchCustomers(params)` — GET `/customers`
  * `getCustomer(id)` — GET `/customers/{id}`
  * `getCustomerContracts(id)` — GET `/customers/{id}/contracts`
  * `getCustomerCards(id)` — GET `/customers/{id}/cards`
  * `getCustomerAccounts(id)` — GET `/customers/{id}/accounts`
  * `getCustomerDocuments(id)` — GET `/customers/{id}/documents`
  * `getCustomerContacts(id)` — GET `/customers/{id}/contacts`

---

## 8. Customer Search Page

* [x] create `frontend/src/pages/Customers.jsx`
  * search bar with mode selector: `Name / National ID / Card / Account`
  * additional filters: `Status`, `Segment` (collapsible filter row)
  * results table: Name, National ID, Mobile, Status, Segment, Branch
  * click row → navigate to `/customers/{id}`
  * pagination controls
  * empty state: prompt user to search
  * loading skeleton during fetch
  * 503 error state: "No active database connection configured"

---

## 9. Customer Detail Page

* [x] create `frontend/src/pages/CustomerDetail.jsx`
  * customer header: full name, national ID, mobile, email, segment, status, branch
  * tab bar: Contracts | Cards | Accounts | Documents | Contacts
  * each tab lazy-loads its data on first activation
  * tabs do not re-fetch on subsequent visits (cached in component state)
  * loading spinner per tab
  * back button → returns to search page preserving last search state

* [ ] create `frontend/src/components/customer/CustomerSearchBar.jsx` _(not created — search bar is inline in Customers.jsx)_
* [ ] create `frontend/src/components/customer/CustomerResultsTable.jsx` _(not created — results table is inline in Customers.jsx)_
* [ ] create `frontend/src/components/customer/CustomerHeader.jsx` _(not created — header is inline in CustomerDetail.jsx)_
* [x] create `frontend/src/components/customer/tabs/ContractsTab.jsx`
* [x] create `frontend/src/components/customer/tabs/CardsTab.jsx`
* [x] create `frontend/src/components/customer/tabs/AccountsTab.jsx`
* [x] create `frontend/src/components/customer/tabs/DocumentsTab.jsx`
* [x] create `frontend/src/components/customer/tabs/ContactsTab.jsx`

---

## 10. Routing & Menu

* [x] add routes in `frontend/src/App.jsx`:
  * `customers` → `Customers.jsx` _(path is `/customers`, not `/customer/search`)_
  * `customers/:id` → `CustomerDetail.jsx`
* [x] add seed menu items via `menu_seed.py` — already present under `issuing` group (`/customers`, permission: `customers.list`)

---

# Oracle Query Risks & Mitigations

| Risk | Mitigation |
|---|---|
| `LIKE '%q%'` full-table scan | Use `LIKE 'q%'` or Oracle Text index; never leading wildcard on large columns |
| `UPPER(col)` bypasses index | Create function-based index `ON customers(UPPER(last_name))` |
| `COUNT(*)` on 10M+ rows | Only count on page 1; skip on subsequent pages |
| `IN` list > 999 items | Chunk into batches of ≤ 999 for Oracle compatibility |
| Deep pagination (page > 200) | Cap at page 200 or switch to keyset (`after_id`) pagination |
| N+1 on linked entity counts | Use aggregation subquery or computed column — never loop queries |
| Unbounded results | Require ≥ 3 chars in query; hard cap results at 200 rows |
| Slow connection per request | Cache SQLAlchemy engine by `connection_id`; invalidate on deactivate/update |

---

# Acceptance Criteria

* [x] search returns results from the active external database connection
* [x] search rejects empty input with 400
* [x] search rejects input shorter than 3 characters with 400
* [x] `GET /customers` returns 503 if no active DB connection is configured
* [x] card numbers are always masked (last 4 digits only)
* [x] account balances are hidden from `viewer` role (balance field is `null`)
* [x] customer detail tabs load lazily (no data until tab is clicked)
* [x] pagination total is computed only on page 1
* [x] all queries are Oracle-compatible
* [x] no hardcoded external DB credentials anywhere in code
* [x] engine cache invalidates when active connection changes

---

# Files to Create

```
backend/app/db_business.py
backend/app/models_business.py
backend/app/repositories/customer_repository.py
backend/app/repositories/customer_contract_repository.py
backend/app/repositories/customer_card_repository.py
backend/app/repositories/customer_account_repository.py
backend/app/repositories/customer_document_repository.py
backend/app/repositories/customer_contact_repository.py
backend/app/services/customer_service.py
backend/app/routers/customer.py

frontend/src/services/customerApi.js
frontend/src/pages/Customers.jsx
frontend/src/pages/CustomerDetail.jsx
frontend/src/components/customer/CustomerSearchBar.jsx
frontend/src/components/customer/CustomerResultsTable.jsx
frontend/src/components/customer/CustomerHeader.jsx
frontend/src/components/customer/tabs/ContractsTab.jsx
frontend/src/components/customer/tabs/CardsTab.jsx
frontend/src/components/customer/tabs/AccountsTab.jsx
frontend/src/components/customer/tabs/DocumentsTab.jsx
frontend/src/components/customer/tabs/ContactsTab.jsx
```

# Additional Tasks
- [x] Link this page to customer menu item (under `issuing` group in menu_seed.py)
- [x] Routes registered in App.jsx
- [x] architecture.md updated in `docs/phases/phase-05/`

## Remaining / Deferred
- [ ] Extract `CustomerSearchBar.jsx` as standalone component (currently inline in Customers.jsx)
- [ ] Extract `CustomerResultsTable.jsx` as standalone component (currently inline in Customers.jsx)
- [ ] Extract `CustomerHeader.jsx` as standalone component (currently inline in CustomerDetail.jsx)
- [ ] `GET /customers/{id}/accounts` — consider returning 403 for `viewer` role instead of hiding balance field only