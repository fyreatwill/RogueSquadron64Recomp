# NEXT work unit — attribute the writer of the producer source slot

HYPOTHESIS-ID: m5-output-state-contract-boundary

Session 3456 selected producer/input: at `0x800645A8`, both routes use source
pointer `0x801E8710`, but the first ordered nonzero loaded `s0` differs
(`retail=0x801B4F00`, `port=0x801B5E70`). Attribute who writes that source slot.

Competing hypotheses and discriminating outcomes:

- `H-PortWriter`: a port writer at or before `0x800645A8` supplies the differing
  word at `0x801E8710`; selects a port-side producer contract defect.
- `H-RetailWriter`: retail alone writes the differing value before the load;
  selects a legitimate route/input difference rather than a port writer bug.
- `H-AddressDivergence`: the source pointer or ordered writer/load join differs;
  selects address/ordering before value comparison.
- `H-ControlFailure`: the whole-RDRAM and four-PC controls do not fire in the
  same run; the result is unevaluable and the control must be repaired.

Ask the retail oracle first: use a whole-RDRAM positive control plus a
phase-gated write watch for physical `0x001E8710:0x001E8714`, and retain the
`0x800645AC` execution watch. Then add the matching phase-scoped port writer
table in one build, preserving the existing positive-control marker. The
discriminator is the writer PC/value at the first joined ordinal: port writer
selects `H-PortWriter`, retail-only writer selects `H-RetailWriter`, an
unmatched source address selects `H-AddressDivergence`, and missing controls
selects `H-ControlFailure`.
