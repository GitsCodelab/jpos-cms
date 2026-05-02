# Switch Integration Rules

Last updated: 2026-05-03

## Separation of Responsibility

- External switch project: real-time transaction switching and ISO network behavior.
- This CMS project: monitoring, reconciliation, settlement, fraud operations, and admin controls.

## Integration Contract Expectations

Upstream should provide stable, replay-safe records containing:
- transaction unique id / external reference
- processing timestamps
- final response code/status
- amount/currency/type
- source system/channel metadata

## CMS-side Rules

- Never treat pending records as final reconciliation outcomes.
- Preserve original external references for traceability.
- Keep write paths idempotent for imported transaction events.
- Track data lineage: source system + import timestamp.

## Error Handling Rules

- ingestion failures must be auditable
- duplicate imports should be detectable and non-destructive
- partial failures should not corrupt reconciliation state
