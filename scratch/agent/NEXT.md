# NEXT work unit (s2419) — repair the port guest task-pointer witness

HYPOTHESIS-ID: m5-phase-transition-identity

## Work unit

Repair only the guest task-pointer witness used by the existing observation-
only handoff table. The submitter and audio dispatcher are different threads,
so replace the submitter TLS handoff with a shared, synchronized guest-pointer
witness; retain the phase, ordinal, row, data pointer, size, and
`data_ptr+0x100` fields unchanged. Build once and rerun the qualified route
with the existing title and hangar controls. Do not change runtime behavior or
add an output remap.

## Competing hypotheses and discriminator

- H-SharedPointerValid: both phase controls pass and the repaired pointer is
  stable at the guest task address while the phase/data table remains usable.
- H-PortDiffersAtHandoff: both controls pass and the repaired table still has
  extra phase-local data pointers or sizes beyond the retail relation.
- H-PortRouteInvalid: either route control fails, so no port null is usable.
- H-PortProbeMisarmed: the positive task/phase control does not fire; fix the
  probe before interpreting a null.

The discriminator is the complete same-run phase-keyed table plus a nonzero
guest-task-pointer positive control. Select H-SharedPointerValid only if both
route controls and the pointer control fire; select H-PortDiffersAtHandoff if
they fire but the phase/data relation still differs. A missing control selects
a route/probe-invalid hypothesis, not a missing writer. Do not interpret
zero-valued payloads as identity.

## Exact commands

Use the existing qualified port driver and its phase-gated M5 task-contract
logging. Repair the pointer witness, build once, and
run one capture with `ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1
ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1`, retaining the independent title and
hangar markers. Capture under `scratch/agent/s2418_port_handoff/`; kill the
game with SIGKILL. Expected retail reference: title rows use
`data_ptr=0x80173B20` and hangar rows use `data_ptr=0x80173CB0`, with task
pointer `0x80149470`; use observed port values rather than forcing them.
