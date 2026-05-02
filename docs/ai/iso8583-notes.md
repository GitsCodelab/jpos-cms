# ISO 8583 Notes for CMS Context

Last updated: 2026-05-03

## Important Context

This repository does not implement full ISO 8583 online switching.
ISO 8583 parsing/authorization/network exchange is handled by an external jPOS switch project.

## What CMS Should Care About

- persisted transaction outcomes and references
- reconciliation identifiers
- settlement classifications
- operational/audit metadata for investigations

## Recommended Data Mapping (Conceptual)

When ingesting switch outputs, keep these fields normalized in CMS storage:
- message type indicator (if provided by upstream)
- processing code
- amount and currency
- retrieval reference / trace fields
- response code and final status
- terminal/merchant/channel context

## Non-goals in this repo

- raw online message routing
- direct network protocol handling
- switch key management and HSM integration

Keep CMS focused on post-transaction visibility and operations.
