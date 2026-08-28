# NEXT work unit (s2978) — RESUME of s2977

HYPOTHESIS-ID: m5-route-preparation-port-comparison

## Context

s2977 was cut off before any experiment ran. This is a full restart of the
same work unit. No s2977 artifact exists; start from scratch.

## Unit

Implement one bounded phase-scoped port measurement for route preparation at
the port-side guest PC. Retain the same-run positive control. Capture route
predecessor, arguments, and live VI width/origin in title (`1024 @
0x00790400`) and hangar (`512 @ 0x006AB400`) phases. Do not change the
predicate.

The existing port instrument is `rs64_m5_route_prepare_inputs` in
`src/main/upstream_compat.cpp:846`, driven by `ROGUESQ_LOG_M5_ROUTE_PREPARE`.
Check whether it already logs predecessor and phase fields adequate to compare
with the s2976 retail table (all 5,204 rows had predecessor `0x80033300`). If
so, no new probe is needed — just run with the env var set, a title+hangar
phase gate, and the positive control.

## Competing hypotheses and discriminator

- H-port-route-matches: port executes the route call in both title/hangar
  phases with predecessor matching retail `0x80033300`.
- H-port-route-absent: port route call never fires in title/hangar despite
  reaching those phases (matching s2972/s2973 results).
- H-port-predicate-mismatch: port executes the route call but predecessor or
  argument fields differ from the retail row.

The discriminator: one same-run table of port route-PC executions filtered to
target phases, compared against s2976's retail table. Phase controls must be
reached (title and hangar VI must fire). Positive control must pass.

## Commands

1. Read `src/main/upstream_compat.cpp` around line 846 to confirm the
   existing route-prep log format (does it include predecessor and phase?).

2. If the existing instrument is sufficient:
   ```
   ROGUESQ_LOG_M5_ROUTE_PREPARE=1 ROGUESQ_AUTOPILOT=1 \
   ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
   ROGUESQ_PROBE_PHASE_WIDTH=1 \
   zsh tools/lle_soak.sh 120
   ```
   Save to `scratch/agent/s2978_m5_route_port/`.

3. If the existing instrument lacks predecessor or phase: add those fields,
   export the submodule patch (`./submodule-patches/export.sh`), rebuild
   (`DEVELOPER_DIR=... cmake --build build --target RecompiledFuncs`), then
   run the same soak.

4. Record the positive-control count, phase-gate fires, route rows, and
   selected hypothesis in `scratch/agent/s2978_m5_route_port/RESULTS.md`.

## Expected discriminating outcomes

- Phase controls reached + zero route rows → selects H-port-route-absent.
- Phase controls reached + rows with predecessor `0x80033300` → selects H-port-route-matches.
- Phase controls reached + rows with different predecessor → selects H-port-predicate-mismatch.
- Positive control fires but phase controls not reached → unevaluable (route stall persists).
