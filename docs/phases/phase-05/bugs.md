# bugs

## Open bugs

## Closed bugs
- [x] "Open full page" now opens in a maximized modal — Ant Design `Modal` (100vw, top=0) renders `CustomerDetail` with `isModal` prop; maximize/restore toggle in modal header
- [x] Cards tab — "Show PAN" / "Hide PAN" toggle button reveals clear card number (admin/operator only); viewer role gets `null` from backend; fetches `?include_pan=true` on demand
- [x] `GET /customers?q=SABRY+HEBA+MOURAD` returned 500 — two root causes:
  1. Engine used `oracle+cx_oracle` driver (not installed) → fixed to `oracle+oracledb` (python-oracledb thin mode)
  2. `status` parameter in `search_customers()` shadowed the `fastapi.status` module → fixed by aliasing import as `http_status`
  - Additionally: Oracle schema prefix `MAIN` was missing → fixed via `schema_translate_map` read from active connection's `schema_name` field
- [x] `GET /customers?q=mas` returned 500 — root cause: models mapped to non-existent tables (`customers`, `customer_cards`, etc.). Fixed by:
  1. Remapped `Customer` → `MAIN.PRD_CUSTOMER`, `CustomerCard` → `MAIN.ISS_CARD`, `CustomerContract` → `MAIN.PRD_CONTRACT`
  2. Rewrote `customer_repository` with raw SQL joining `PRD_CUSTOMER → ISS_CARD → ISS_CARDHOLDER` for name search
  3. Rewrote card/contract repositories with raw SQL on real Oracle tables
  4. Schema prefix extracted dynamically from engine's `schema_translate_map` — nothing hardcoded
- [x] Wildcard search — user can now type `*xxx*`, `xxx*`, `*xxx`; `*` is translated to `%` before passing to LIKE
- [x] Customer page default 100 records — `PAGE_SIZE` in frontend and `page_size` default in router changed from 25 → 100
- [x] Contracts tab "Failed to load contracts" — two fixes:
  1. Pydantic `ValidationError`: `open_date` was typed as `date` but Oracle returns `datetime` → changed schema field to `Optional[datetime]`
  2. Query rewritten to use `MAIN.GET_ARTICLE_DESC(CONTRACT_TYPE)` for human-readable type description, joined to `PRD_CUSTOMER`
- [x] Accounts tab "no data" — repository rewritten to query `MAIN.ACC_ACCOUNT JOIN MAIN.PRD_CUSTOMER ON c.ID = a.CUSTOMER_ID`
- [x] Customer view as popup — clicking a row or the eye icon now opens a `CustomerDrawer` (Ant Design Drawer). A "Open full page" button is available in both the drawer header and each row's actions column
