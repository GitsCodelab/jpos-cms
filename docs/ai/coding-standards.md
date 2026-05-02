# Coding Standards

Last updated: 2026-05-03

## General

- Prefer readability over cleverness.
- Keep functions small and single-purpose.
- Use descriptive names for domain concepts.
- Add concise comments only where logic is non-obvious.

## Backend (FastAPI + SQLAlchemy)

- Use type hints for function signatures.
- Keep routers thin; push logic into services.
- Use dependency injection for DB sessions and auth payloads.
- Use Pydantic schemas for request/response boundaries.
- Normalize datetime handling (UTC) consistently.
- Wrap DB writes with error handling and rollback on failure.

### Auth-specific

- Use hashed passwords only.
- Maintain token revocation behavior via JTI blacklist.
- Audit login attempts for success/failure.

## Frontend (React + Ant Design)

- Keep route and layout concerns separated.
- Centralize API logic in `src/services`.
- Keep menu metadata in `src/config/menuConfig.jsx`.
- Avoid duplicating state between components.
- Persist only necessary client state in localStorage.

## Documentation

- Every phase file must include: scope, status, done, pending, risks.
- API docs must label each endpoint as implemented or planned.
