# NEXT work unit — qualify the source-slot writer value

HYPOTHESIS-ID: m5-output-state-contract-boundary

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

Ask the retail oracle first: use the existing whole-RDRAM control and source
watch, adding post-store word/value capture for the eight observed writer PCs
in the title bucket. Then build the matching port arm with actual post-store
value capture at every source-slot writer, preserving the existing schema
positive control. The discriminator is the first phase/PC/ordinal writer
value joined to the producer load: retail-only value selects `H-RetailValue`,
different shared-writer value selects `H-SharedValue`, a port-only value
selects `H-PortValue`, and missing controls selects `H-ControlFailure`.
