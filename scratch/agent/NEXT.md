# NEXT work unit (s2418) — compare the retail-selected task/data handoff on port

HYPOTHESIS-ID: m5-phase-transition-identity

## Work unit

Add one observation-only port table for the retail-selected relation: phase
(`1024/0x00790400` versus `512/0x006AB400`), task pointer, task ordinal/row,
`data_ptr`, `data_size`, and `data_ptr+0x100`. Build once and run the qualified
route with the existing title and hangar controls. Do not change runtime
behavior or add an output remap.

## Competing hypotheses and discriminator

- H-PortMatchesRetail: port emits the same phase-specific task/data relation.
- H-PortDiffersAtHandoff: port reaches both phases but changes task/data
  identity; the transition field remains open.
- H-PortRouteInvalid: either route control fails, so no port null is usable.
- H-PortProbeMisarmed: the positive task/phase control does not fire; fix the
  probe before interpreting a null.

The discriminator is the complete same-run phase-keyed table. Select
H-PortMatchesRetail only if both route controls pass and the port reproduces
the retail task/data relation; select H-PortDiffersAtHandoff if both controls
pass but the relation differs. A missing control selects a route/probe-invalid
hypothesis, not a missing writer. Do not interpret zero-valued payloads as
identity.

## Exact commands

Use the existing qualified port driver and its phase-gated M5 task-contract
logging. Add the table in the fixup/instrumentation source, build once, and
run one capture with `ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1
ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1`, retaining the independent title and
hangar markers. Capture under `scratch/agent/s2418_port_handoff/`; kill the
game with SIGKILL. Expected retail reference: title rows use
`data_ptr=0x80173B20` and hangar rows use `data_ptr=0x80173CB0`, with task
pointer `0x80149470`; use observed port values rather than forcing them.
