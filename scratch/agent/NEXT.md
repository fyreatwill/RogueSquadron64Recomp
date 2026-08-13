# NEXT work unit (attribute the drawIndexedTri G_CYC_COPY caller)

HYPOTHESIS-ID: m3-drawindexed-copy-cycle

Perform one phase-gated diagnostic build/run that records the active GBI,
dispatch opcode, triangle-handler family, and RDP/RSP cycle values immediately
before every `drawIndexedTri` call and at the assertion. Keep the existing
positive triangle/provenance control in the same run. Do not change behavior or
add a mitigation.

Competing hypotheses and discriminator:

- H-copy-cycle-legitimate: a documented Factor 5 triangle opcode reaches the
  helper while copy mode is intentionally active.
- H-cycle-state-stale: RSP and RDP cycle values diverge or a prior copy writer
  remains active across the caller transition.
- H-wrong-handler: inherited 0xB1 TRI2 or another malformed dispatch reaches the
  helper instead of Factor 5's 0xB4/0xBF path.

Discriminator: a positive control must show the marker fires for a normal
triangle. A 0xB4/0xBF caller with synchronized copy mode selects
H-copy-cycle-legitimate; divergent RSP/RDP values or an unmatched prior setter
select H-cycle-state-stale; 0xB1/unknown dispatch or a malformed handler
selects H-wrong-handler. Only after this attribution is a parser retry or
behavior change justified.

Exact execution: add one regeneration-safe, phase-scoped diagnostic batch;
build Debug; run the existing phase-gated recipe from `build/` with the
positive control and crash capture enabled; compare caller/opcode/cycle rows.
