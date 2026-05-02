# Fintech CMS Architecture

Last updated: 2026-05-03

## 1) High-Level View

jPOS CMS is an operational control plane for payment operations.
It sits downstream of transaction switching and focuses on post-transaction workflows.

Primary capabilities targeted:
- reconciliation workflows
- settlement monitoring
- fraud monitoring
- operations/configuration dashboards

## 2) Components

### Backend
- FastAPI app bootstrap and routing (`app/main.py`)
- SQLAlchemy models (`app/models.py`)
- Auth service (`app/services/auth.py`)
- Pydantic schemas (`app/schemas.py`)

### Frontend
- React app shell with authentication gate
- Ant Design layout and enterprise sidebar
- Axios API client with JWT interceptor

### Persistence
- Current local runtime: SQLite (compose override)
- Oracle-ready and PostgreSQL-ready architecture in code/config

## 3) Request Flow

1. User logs in via frontend `POST /api/auth/login`.
2. Vite proxy forwards to backend `/auth/login`.
3. Backend validates credentials via DB user table.
4. Backend creates session row + JWT (with JTI).
5. Frontend stores token and user object in localStorage.
6. Subsequent API calls include `Authorization: Bearer <token>`.

## 4) Security Architecture

Implemented:
- JWT token validation dependency
- Per-token revocation via JTI blacklist
- Session revocation tracking
- Login audit trail
- Password hashing via bcrypt (fallback path exists)

Gaps:
- no refresh-token flow currently wired to routes
- no rate limiting enabled in running middleware
- role/permission enforcement beyond auth endpoints is pending

## 5) UI Architecture

- `App.jsx`: login gate and routing shell
- `MainLayout.jsx`: top header + sidebar + content outlet
- `Sidebar/index.jsx`: menu/bookmarks/search experience
- `menuConfig.jsx`: centralized navigation metadata (permission-ready)
- `PlaceholderPage.jsx`: interim target for unimplemented pages

## 6) Delivery State

Implemented now:
- Auth API and session model
- Login/logout/me/change-password/session endpoints
- Full enterprise menu hierarchy in frontend config

In progress / pending:
- backend domain APIs (transactions/reconciliation/fraud/settlement)
- role-filtered menu endpoint
- page-level frontend modules replacing placeholders

## 7) Deployment Topology (Local)

Compose services:
- `jpos-cms-backend` on host `:8002`
- `jpos-cms-frontend` on host `:5174`

Backend startup behavior:
- runs `init_db()` on startup
- creates schema tables
- seeds default admin if absent
