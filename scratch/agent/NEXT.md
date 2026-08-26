# NEXT work unit (s2399) — locate accepted-preparation identity clearing

HYPOTHESIS-ID: m5-image-stage-route-order-perturbation

## Work unit

Use the existing route-order/stage-call instrumentation in one new bounded
capture. Keep the qualified LLE route, image arm, missing-function suppression,
and `PROBE_PHASE_WIDTH=1024`. Add one phase-keyed join/reducer over Arm B's
accepted `[m5-route-prepare]` rows and subsequent `[m5-stage-call]` rows,
including the identity's `route_valid`, `prepare_seq`, route ordinal/row, and
the call's guest PC/callsite if already available. Do not change task data,
audio, gate, fallback, dispatch, VI, output behavior, or mitigation.

## Competing hypotheses and discriminator

- H-IdentityClearedBeforeStage: an accepted target preparation is followed by
  a stage call with the identity cleared before entry.
- H-IdentityNotConsumedByStage: accepted preparation remains observable, but
  the stage call reads a separate/non-route identity source.
- H-TargetPreparationIsUnrelated: accepted rows are from unrelated work and
  do not temporally precede the target stage calls.

The discriminating table is phase-keyed and has one row per retained stage
call: preceding accepted preparation sequence, delta/order, identity-valid
state, route ordinal/row, stage callsite/PC, and arm. A consistent immediate
accepted predecessor followed by `route_valid=0` selects clearing; an accepted
identity with invalid stage state selects separate-source use; no accepted
predecessors selects unrelated preparation. The existing whole-RDRAM oracle
and s2392 exact-window controls remain prerequisites before adding or trusting
any new field.

## Required controls

Both the logger-off and logger-on arms must show dispatch activity and title
origin `0x00790400`; phase-gate all counts with `PROBE_PHASE_WIDTH=1024` and
kill each run with SIGKILL. The s2398 two-arm result is the reachability
control; do not spend another iteration re-testing logger perturbation.
