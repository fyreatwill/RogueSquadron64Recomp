# NEXT work unit (independently capture late bridge range association)

HYPOTHESIS-ID: m3-e9-command-boundary

Change the bridge-side E9 boundary record budget from lifetime-scoped to
task-scoped, keeping the existing parser command/pending records and all
behavior unchanged. Build once, then run the established phase-gated VI-1024
recipe with the existing four E9 provenance controls and
`ROGUESQ_LOG_E9_BOUNDARY=1`.

Competing hypotheses and discriminator:

- H-range-association: late bridge E9 slots have no matching parser call range
  for the same task/submit serial.
- H-parser-call-mismatch: late bridge slots have matching parser call ranges,
  but parser records were associated with the wrong task or serial.
- H-bridge-record-loss: late bridge slots are absent because the bridge record
  budget or emission path drops them.

Late bridge records with no same-serial parser range select
H-range-association; same-serial parser ranges select H-parser-call-mismatch;
missing late bridge records despite live controls select H-bridge-record-loss.
The established span-covered population is not re-litigated. Require VI 1024
and all four positive controls before interpreting any null.
