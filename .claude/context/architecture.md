# jPOS CMS Architecture Context (Current Snapshot)

Last updated: 2026-05-03

## 1) System Purpose

jPOS CMS is an operations and monitoring platform for card/payment operations.
It focuses on:
- reconciliation
- settlement monitoring
- fraud monitoring
- operational dashboards and configuration

Important boundary:
- This repository is NOT the transaction switch.
- The jPOS/Q2 switch runs in a separate project and populates source databases.

## 2) Technology Stack

Backend:
- FastAPI
- SQLAlchemy ORM
- JWT auth (PyJWT)
- bcrypt password hashing

Frontend:
- React + Vite
- Ant Design
- Axios
- React Router

Runtime:
- Docker Compose
- Backend container: Python 3.12
- Frontend container: Node 18

## 3) Runtime Topology

From docker-compose:
- Service `jpos-cms-backend`
  - Exposes host port `8002` -> container `8000`
  - Volume mount: `./backend:/app` (live code)
  - Current DB mode in compose: SQLite (`sqlite:////app/jpos_cms.db`)
- Service `jpos-cms-frontend`
  - Exposes host ports `5174` and `3001`
  - Runs `npm install && npm run dev`
  - Vite proxy rewrites `/api/*` -> backend without `/api`

## 4) Backend Architecture

Current layering in code:
- Routers: `backend/app/routers`
- Services: `backend/app/services`
- Repositories: base repository scaffolding exists
- Models: `backend/app/models.py`
- Schemas: `backend/app/schemas.py`

Current endpoint implementation state:
- Fully implemented: auth router (`/auth/*`)
- Implemented utility routes: `/health`, `/ping`
- Stub routers (registered but no endpoints yet):
  - `/transactions`
  - `/reconciliation`
  - `/fraud`
  - `/settlement`
  - `/net`
  - `/dashboard`
  - `/config`

## 5) Authentication Model

Implemented in Phase 1:
- DB-backed users (`users` table)
- JWT with `sub`, `role`, `jti`, `exp`, `iat`
- Session table (`user_sessions`) for active/revoked tracking
- Token blacklist table (`token_blacklist`)
- Login audit table (`login_audit`)
- Default seeded admin on startup if missing:
  - username: `admin`
  - password: from `AUTH_PASSWORD` (defaults to `admin123`)

Auth API implemented:
- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/logout`
- `POST /auth/change-password`
- `GET /auth/sessions`
- `POST /auth/revoke-all-sessions`
- `POST /auth/cleanup-tokens` (admin-only)
- `GET /auth/health`

## 6) Data Model Coverage

Main model groups defined:
- Transactions
- Reconciliation runs and unmatches
- Fraud rules and alerts
- Settlement batches and statements
- Report jobs
- Users/sessions/audit/blacklist

Note:
- Models and schemas are broadly defined for enterprise scope.
- Only auth flows are currently wired through live router endpoints.

## 7) Frontend Architecture

Main composition:
- Login gate in `App.jsx`
- Authenticated layout in `components/MainLayout.jsx`
- Sidebar navigation in `components/Sidebar/index.jsx`
- Placeholder route renderer in `pages/PlaceholderPage.jsx`

Sidebar capabilities implemented:
- deep nested menu tree
- collapse/expand
- search tab
- bookmarks tab persisted in localStorage
- route-aware selected/open states

Routing status:
- all non-login paths currently route to placeholder pages
- default authenticated route redirects to `/monitoring/notifications`

## 8) Configuration and Security

Environment highlights (`backend/.env` + compose):
- JWT secret and expiry configured
- CORS origins configured for local dev ports
- compose forces SQLite for current local environment

Security caveat:
- `security.py` keeps a legacy env-based `authenticate_user()` helper, but auth router uses DB-backed `AuthService`.

## 9) Known Gaps / Next Work

High-priority next steps:
- Implement real business endpoints for non-auth routers
- Add role/permission filtering API for menu (`GET /menu`)
- Connect sidebar routes to actual pages and APIs
- Add breadcrumb component and recently visited items
- Add migration strategy from SQLite dev mode to PostgreSQL/Oracle target

## 10) How to Keep This File Accurate

When code changes, update this file in the same PR and verify:
- router endpoint list
- compose runtime topology
- auth/session model behavior
- implemented vs planned features
