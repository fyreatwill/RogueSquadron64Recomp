# NEXT work unit (post-sec2 reachability stability soak)

HYPOTHESIS-ID: m3-postsec2-reachability

The s789 writer audit identified RT64 garbage-SETCIMG writeback as the named
writer for the allocator corruption and left the s787 tile-copy assertion
independent. Do not add a mitigation from either crash.

## Competing hypotheses

- H-parser-chain: the post-sec2 parser/control-flow path is the remaining
  cause of the FULL_SYNC plateau. Prediction: a stable run reaches the
  post-sec2 provenance gate and records authoritative parser E9/FULL_SYNC
  advances.
- H-prechain-transient: pre-chain failures still prevent measurement.
  Prediction: positive controls fire but the run dies before a usable
  post-sec2 parser sample.
- H-writer-co-gate: the named garbage-SETCIMG writeback remains coupled to
  the recovery path and changes reachability. Prediction: same-run phase
  telemetry correlates the writeback/restore events with the post-sec2 gate.

## Discriminating measurement

One phase-gated stability soak using the established low-noise post-sec2
recipe, with all passive provenance controls and the existing freelist
writeback/restore telemetry enabled. The discriminating measurement is a
usable post-sec2 parser-chain sample after VI width 1024: parser E9/FULL_SYNC
advances select H-parser-chain; positive controls plus a pre-gate crash select
H-prechain-transient; a stable gate with writeback/restore correlation selects
H-writer-co-gate. A null without the positive controls is invalid.

## Exact audit

1. Run the existing low-noise recipe from `scratch/agent` with its phase gate;
   do not use a stopwatch and kill with SIGKILL if the watchdog expires.
2. Require repeated `emit=1`, `raw=1`, `dispatch=1`, and `match=1` controls.
3. Compare parser-chain counts and writeback/restore correlation in that same
   run; do not infer from an animating-scene cross-run A/B.

Expected outcomes: a controlled post-sec2 parser sample selects H-parser-chain;
an early death with controls selects H-prechain-transient; a stable gate with
same-run writeback correlation selects H-writer-co-gate.
