# NEXT work unit (s2882) — M5 pre-title route-order/stage-call discriminator

HYPOTHESIS-ID: m5-pretitle-route-order

## Work unit

Run one ground-truth-first route discriminator to locate the pre-title stop
that prevented M5 Step 1 from being evaluated. Use the retail oracle positive
control plus both same-build port arms and record the complete phase-gated
route-order/stage-call table. Do not change runtime behavior or interpret
downstream audio nulls unless title or hangar is reached.

## Competing hypotheses and discriminator

- H-RouteOrder: the pre-title route diverges at a route-order edge; ordering
  or identity differs before VI 640.
- H-StageCall: route-order is shared, but one stage-call source/return is
  absent or reordered in the port.
- H-RecipeState: route-order and stage-call rows match, so another state/input
  boundary causes the stop.

The single discriminating measurement is one phase-keyed table for retail and
both port arms containing every route-order and stage-call edge, with caller,
callee/source, ordinal, return, and VI phase. The whole-RDRAM positive control
and retail title/hangar transitions must be present; a port pre-title stop is
the result, not evidence about audio.

## Exact next commands

1. Build once: `cmake --build build --config Debug --target RogueSquadron64Recomp`.
2. Use `scratch/agent/run_s2658_m5_task_output_fields.sh` as the base, add
   `ROGUESQ_LOG_M5_ROUTE_ORDER=1` and `ROGUESQ_LOG_M5_STAGE_CALLS=1`, and run
   the oracle plus image/silent arms from `build/`. Use SIGKILL after the
   bounded capture.
3. Write the table and selection to
   `scratch/agent/s2882_m5_pretitle_route_order/RESULTS.md`.

## Expected outcomes

- Matching route-order rows with different stage-call rows selects
  H-StageCall.
- Matching rows select H-RecipeState.
- No route match leaves Step 1 audio unevaluable and authorizes no behavior
  change.
