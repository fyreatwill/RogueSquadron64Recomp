# Next work unit: qualify the M5 route before another writer census

HYPOTHESIS-ID: m5-route-qualification-4020

Competing hypotheses:

- H1: declared/real is the stable real-audio route; it reaches both target VIs
  while legacy/real fails or diverges before them.
- H2: legacy/real is the stable real-audio route; it reaches both target VIs
  while declared/real fails or diverges before them.
- H3: both real-audio arms qualify, so the prior route failure was schedule or
  run-sensitive and cannot select a writer class.
- H4: declared/silent is the only arm that qualifies, showing the failure is
  tied to real-audio execution rather than staging size.

Discriminator: one same-build, concurrent four-arm capture with retail,
declared/real, declared/silent, and legacy/real; require the retail whole-RDRAM
positive control plus title VI 1024 and hangar VI 512 controls, and compare
phase-scoped source/audio/task rows and crash markers for all three port arms.
H1/H2 require exactly one real arm to reach both target VIs while the other
fails before them; H3 requires both real arms to reach both; H4 requires the
silent arm alone to reach both. A retail null or a port arm without both phase
controls is not a writer-class result.

Commands: use the existing checked-in route recipe, run all four arms
concurrently from `build/` with the existing source, audio-stage, RSP-source,
and phase controls, then record the phase-gated comparison. Do not add a
writer census or mitigation in this iteration.
