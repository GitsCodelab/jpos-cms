# AI Architecture Rules

Last updated: 2026-05-03

These rules are optimized for this repository and should be followed by AI assistants.

## 1) Boundary Rules

- Treat this project as CMS/monitoring, not the switch runtime.
- Do not introduce jPOS switch execution logic inside this backend.
- Assume external systems populate source transaction/settlement data.

## 2) Layering Rules

- Routers: request/response orchestration only.
- Services: business logic and workflows.
- Repositories: data access queries and persistence concerns.
- Models/Schemas: data shape and validation contracts.

Never place reconciliation/fraud/settlement business decisions in routers.

## 3) API Design Rules

- Keep existing endpoint contracts backward compatible.
- Use explicit response models for all public routes.
- Return consistent error shape and proper HTTP status codes.
- Support pagination for large list endpoints.

## 4) Data Access Rules

- Avoid N+1 query patterns.
- Prefer bulk operations for reconciliation workloads.
- Keep SQLAlchemy relationships explicit where multiple FKs exist.
- Preserve Oracle-compatible design choices when adding SQL features.

## 5) Auth/Security Rules

- Use JWT validation dependency for protected endpoints.
- Treat JTI blacklist and session revocation as first-class behavior.
- Never log plain credentials or secrets.
- Validate all incoming payloads with Pydantic schemas.

## 6) Frontend Rules

- Keep API calls in service modules, not in many scattered components.
- Preserve menu configuration as a centralized source of truth.
- Keep role/permission metadata in menu items for future RBAC filtering.
- Provide loading and error states for all real API pages.

## 7) Documentation Rules

- Update docs together with code changes.
- Distinguish clearly between IMPLEMENTED and PLANNED behavior.
- Do not present roadmap items as shipped features.
