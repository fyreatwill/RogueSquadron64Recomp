# NEXT work unit — compare selector load/writer rows against retail

HYPOTHESIS-ID: m5-selector-load-writer-comparison

Session 3494 qualified the real-audio route on retry: title and both selector
controls fired, with 1,024 load rows and 1,024 writer rows. Evidence is in
`docs/M5-S3494-REAL-AUDIO-ROUTE.md` and
`scratch/agent/s3493_m5_real_selector/`.

Competing hypotheses and discriminating outcomes:

- `H-SelectorParity`: title-gated port selector source/value families match
  the independently captured retail families.
- `H-SelectorSourceDivergence`: both controls fire, but the first stable
  source/value family differs between port and retail.
- `H-SelectorRouteNull`: one selector control or its title rows are absent in
  the new port capture despite the route qualification.

Discriminating measurement: one batched port/retail selector-load/writer
comparison keyed by title origin, writer PC, source/value family, and
phase-scoped ordinal. Positive controls must fire in both runtimes. Matching
families select parity; a first stable mismatch selects source divergence;
missing controls make the result unevaluable and require route repair.

Exact starting point: reuse the existing selector capture and independent
retail task-dispatch recipe referenced by Sessions 3490–3493; build all arms
once, then run the controlled comparison. Keep SIGKILL watchdog behavior,
title VI phase gating, and capture paths under `scratch/agent/`.
