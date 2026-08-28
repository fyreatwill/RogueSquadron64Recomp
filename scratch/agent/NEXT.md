# NEXT work unit (s2872) — M5-new-route-state-discriminator

HYPOTHESIS-ID: M5-new-route-state-discriminator

## Work unit

Use one source audit and one batched instrument to identify and test a new
post-dispatch route-state discriminator for the persistent port stop at VI
640. The prior recipe drift was restored in both arms and did not reach
hangar. Do not repeat launch/configuration comparisons or interpret downstream
audio nulls.

## Competing hypotheses and discriminator

- H-route-state: a new state/control boundary is responsible for the VI-640
  stop.
- H-dispatch-order: dispatch reaches the known marker but its ordering or
  predecessor differs before the target phase.
- H-input-gate: the restored route still fails because phase-relative input is
  not delivered at the expected caller.

The discriminator is one source-backed table of every post-dispatch state
write/read and predecessor around the VI-640-to-512 transition, with a
phase-scoped positive-control row from the existing dispatch marker. A new
state edge in both arms selects H-route-state; a changed predecessor/order
selects H-dispatch-order; a missing phase-relative input row selects
H-input-gate. If the table has no new edge, pivot to the next distinct source
class rather than adding another diagnostic field.

## Exact command

    rg -n 'm5-route-state|m5-b40-route|ROGUESQ_M4_Y8000_WIDTH|VI 640|VI 512' src RecompiledFuncs tools scratch/agent/s2871_m5_route_repair_discriminator
    rg -n 'post-dispatch|route-state|VI 640|VI 512' docs/CURRENT-TRUTH.md docs/PROJECT-OVERVIEW.md

Then batch the selected state instrumentation into one Debug build and run
both audio arms concurrently with `PROBE_PHASE_WIDTH=512
PROBE_KEYS_FROM_PHASE=1`. Record the state table and phase-gated outcome under
`scratch/agent/s2872_m5_new_route_state_discriminator/`.
