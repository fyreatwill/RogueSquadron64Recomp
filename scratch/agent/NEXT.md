# NEXT work unit — qualify the port route, then source-slot writer value

HYPOTHESIS-ID: m5-output-state-contract-boundary

Session 3458 measured the retail values but could not qualify the port arm.
Session 3457 selected a retail-side writer/route difference: retail writes
`0x801E8710` from eight title-phase PCs, while the port table emitted only the
shared `0x800644B0` and `0x80064524` writers. The current port parity hook
passes zero for its value field, so actual writer-value attribution remains
open. At `0x800645A8`, both routes still use source pointer `0x801E8710`, but
the first ordered nonzero loaded `s0` differs (`retail=0x801B4F00`,
`port=0x801B5E70`).

Competing hypotheses and discriminating outcomes:

- `H-RetailValue`: a retail-only writer stores the word that leads to
  retail's loaded `s0`; selects a retail-side producer/value contract
  difference.
- `H-SharedValue`: the shared writers store different words or order
  differently; selects a shared producer/value divergence.
- `H-PortValue`: a port writer stores the differing word despite the current
  PC-set difference; selects a port-side producer contract defect.
- `H-ControlFailure`: either positive control is absent; the result is
  unevaluable and the control must be repaired.

The retail arm is complete. Run the validated port route with
`ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
ROGUESQ_SPIN_YIELD=1`, preserving `ROGUESQ_LOG_M5_WRITER_PARITY=1` and the
phase-relative title key schedule. First repair/qualify the startup SIGBUS at
guest PC `0x8000834C`; do not alter audio waits, slots, dispatch, clear
behavior, or PCM writeback. The discriminator remains the first
phase/PC/ordinal writer value joined to the producer load: retail-only value
selects `H-RetailValue`, different shared-writer value selects `H-SharedValue`,
a port-only value selects `H-PortValue`, and missing controls selects
`H-ControlFailure`.
