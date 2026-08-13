# NEXT work unit (establish the triangle-handler dispatch positive control)

HYPOTHESIS-ID: m3-drawindexed-copy-cycle

Perform one phase-gated diagnostic build/run that records dispatch of candidate
triangle opcodes 0xB1, 0xB4, and 0xBF before the existing `drawIndexedTri`
breadcrumb. Keep the E9 provenance positive control in the same run. Do not
change behavior or add a mitigation.

Competing hypotheses and discriminator:

- H-no-triangle-dispatch: the recipe never dispatches a candidate triangle
  opcode, so the previous null was only a reachability gap.
- H-factor5-consume-only: 0xB4/0xBF dispatches but the installed handlers do
  not call `drawIndexedTri`.
- H-wrong-handler: 0xB1 dispatches under Factor 5 and reaches inherited TRI2.

Discriminator: the E9 controls must fire, and a candidate dispatch row followed
by a draw row is the required triangle positive control. 0xB4/0xBF without a
draw row selects H-factor5-consume-only, 0xB1 with a draw row selects
H-wrong-handler, and no candidate rows selects H-no-triangle-dispatch. Only
then attempt cycle-state attribution or behavior changes.

Exact execution: add one regeneration-safe, phase-scoped dispatch diagnostic;
build Debug; run the existing phase-gated recipe from `build/` with the E9
positive control and crash capture enabled; compare candidate dispatch rows to
the draw/assert rows.
