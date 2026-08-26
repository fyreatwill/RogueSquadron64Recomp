# NEXT work unit (s2398) — isolate route-order witness reachability perturbation

HYPOTHESIS-ID: m5-image-stage-route-order-perturbation

## State going in

s2397's behavior-neutral route-order witness passed dispatch and stage-call
controls but crashed at `0x8000B650` before title. Its audio-probe-enabled
retry also failed to reach title, while s2396's stage-call-only run reached
title. The target-phase preparation question is therefore confounded by
whether the extra logging changes timing/state or whether the crash is an
independent pre-title route failure.

## Work unit

Run the existing built binary in two same-build arms concurrently for 60
seconds from `build/`: Arm A has the s2396 controls and stage-call witness but
`ROGUESQ_LOG_M5_ROUTE_ORDER=0`; Arm B adds `ROGUESQ_LOG_M5_ROUTE_ORDER=1`.
Capture dispatch, title-origin, crash/abort, stage-call, and preparation-row
counts. Use the s2392 oracle exact-window result as the existing ground-truth
prerequisite; do not change task data, audio, gate, fallback, dispatch, VI,
output behavior, or mitigation.

## Competing hypotheses and discriminator

- H-RouteOrderWitnessPerturbsPath: only Arm B loses title or crashes; the
  added preparation logging changes timing/state.
- H-PreTitleCrashIndependent: both arms lose title with the same pre-title
  crash family; route-order logging is not causal for reachability.
- H-RouteOrderWitnessPreservesRoute: both arms reach title; the s2397 failure
  was a one-off run/setup failure and target-phase ordering can be analyzed
  from Arm B.

The discriminating table is one row per arm: dispatch count, title-origin
control, crash/abort count and last guest PC, stage-call count, preparation
count, accepted-preparation count, and stage-call preparation-sequence joins.
Only an Arm-B-only failure selects logging perturbation; matched pre-title
failures select an independent crash boundary; title in both arms permits the
target-phase ordering analysis.

## Controls and commands

Both arms must show `[audtask-dispatch]` activity; title origin
`0x00790400` is the phase control. Use the built macOS executable from `build/`
with the existing s2396 route controls, then SIGKILL each process after 60
seconds. The s2392 oracle exact-window witness is the ground-truth
prerequisite.
