# API Specification (Current State)

Last updated: 2026-05-03
Base URL (local): `http://localhost:8002`
Proxy path from frontend: `/api/*` -> backend `/*`

## 1) Auth Endpoints (Implemented)

### POST /auth/login
Authenticate user and create a session.

Request:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

Response 200:
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "username": "admin",
    "role": "admin",
    "email": "admin@jpos-cms.local"
  }
}
```

Errors:
- 401 invalid credentials

### GET /auth/me
Requires Bearer token. Returns current profile.

### POST /auth/logout
Requires Bearer token. Revokes current session/token.

### POST /auth/change-password
Requires Bearer token.
Request:
```json
{
  "old_password": "old",
  "new_password": "new_password_min_8"
}
```

### GET /auth/sessions
Requires Bearer token. Returns active sessions.

### POST /auth/revoke-all-sessions
Requires Bearer token. Revokes all sessions for current user.

### POST /auth/cleanup-tokens
Requires Bearer token with admin role. Deletes expired blacklist entries.

### GET /auth/health
Auth service health check.

## 2) System Endpoints (Implemented)

### GET /health
No auth required.

Response:
```json
{
  "status": "ok",
  "service": "jpos-cms-backend",
  "version": "1.0.0"
}
```

### GET /ping
Requires Bearer token.

## 3) Registered but Not Implemented (Router Stubs)

The following routers are mounted but currently expose no business endpoints:
- `/transactions`
- `/reconciliation`
- `/fraud`
- `/settlement`
- `/net`
- `/dashboard`
- `/config`

## 4) Auth Model Notes

JWT payload includes:
- `sub` (username)
- `role`
- `jti`
- `exp`
- `iat`

Server-side revocation uses:
- `user_sessions` table
- `token_blacklist` table

## 5) Planned Additions (Not Yet Implemented)

- `GET /menu` role-filtered menu tree
- business CRUD/list endpoints for transactions, reconciliation, fraud, settlement
- dashboard and monitoring metrics endpoints

Planned additions must be documented as implemented only after route + tests are added.
