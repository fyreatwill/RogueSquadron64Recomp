# Next work unit

HYPOTHESIS-ID: m4-accumulator-retail-witness-revisit

Revisit the parked M4 accumulator boundary with a genuinely new, same-phase
retail witness. Build one batched capture that arms the independent retail
oracle for the VMADH/VGE/store boundary and the port's existing phase-5 M4
rows in the same run recipe; do not add another join key or run a port-only
counter. Require the whole-RDRAM positive control, title `0x00790400`, hangar
`0x006AB400`, and phase-scoped budgets.

Competing hypotheses:

- H-M4-retail-same: retail and port expose the same accumulator/store values
  at the phase-5 boundary; the remaining artifact is downstream or unrelated.
- H-M4-retail-different: retail exposes a different value before the store;
  the divergence identifies the next arithmetic or input boundary.
- H-M4-unreachable: the retail oracle cannot reach the target boundary while
  its whole-RDRAM control fires; this leaves the comparison unevaluable and
  requires a route fix rather than another field.

Discriminating measurement: paired phase-5 rows for the same boundary stages
from the retail oracle and port, with the whole-RDRAM control and both VI
origins positive. Equal pre/post values select H-M4-retail-same; a stable
retail/port mismatch selects H-M4-retail-different; absent target rows with a
firing control select H-M4-unreachable. Build every arm in one instrument and
do not infer from a stopwatch or an unqualified null.

Exact preparation: inspect the existing M4 capture/oracle recipe with
`rg -n 'M4|VMADH|VGE|accumulator' scratch tools docs`; then use the established
phase-gated run wrapper and SIGKILL cleanup. If the oracle cannot be driven to
the boundary, record that as the experiment result rather than adding another
diagnostic field.
