# Substitution — Session 2977 (2026-08-28)

## 1. What specifically stopped the planned work unit

The session hit a turn/usage limit before running any experiment. The planned
work unit (port-side phase-scoped route probe, `m5-route-preparation-port-
comparison`) requires building and running the Debug binary with route-PC
instrumentation. No such build or run occurred.

## 2. Evidence THIS iteration that the unit was actually stopped

- No scratch directory `scratch/agent/s2977_m5_route_port/` exists.
- PORTING-STATE.md contained no Session 2977 entry when this checkpoint
  iteration began.
- `OUTCOME=ADVANCED` and `STATUS=DONE` were written before the exit contract
  was met (session entry missing, no experimental result).
- All submodule +/- diff lines match the stored patches; no new probe was
  exported or committed.

## 3. Single experiment that would refute this blocking explanation

Attempt the identical work unit in the next iteration. If a `RESULTS.md`
appears in `scratch/agent/s2977_m5_route_port/` (or `s2978_...`) with a
positive-control count and at least one phase-tagged route-PC row, the
blocking explanation (turn cap before experiment) is refuted. If the session
again hits the limit before that artifact exists, the pattern repeats and a
human review of the model budget is warranted.
