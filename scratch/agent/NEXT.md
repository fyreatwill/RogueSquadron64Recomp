# NEXT work unit (s1013)

s1012 (static compare-semantics audit): the SGI RSP guide and local VGE
implementation agree that VGE selects `vs` or the selected `vt` lane; it does
not synthesize the observed `-0.5/+0.5` sentinel. The final compare therefore
preserves a value from `v6` or selects a DMEM-0x60 table lane. The numeric-origin
lead moves to the preceding `vmadh v6,v4,v0` accumulator/high-half path. No
mitigation was made. The queued SP-guard soak crashed before its guard record
and remains separate.

HYPOTHESIS-ID: m4-zero-shade-accumulator-origin

## One work unit

Static audit only; no build or run. Trace `vmadh v6,v4,v0` and the RSP
accumulator high-half/saturation rules to explain the four shade lanes entering
the final `vge`. Do not edit generated output.

Competing hypotheses and discriminating measurement:

- `H-accumulator-saturation`: the endpoint pattern is created by accumulator
  high-half saturation.
- `H-v4-v0-arithmetic`: the endpoint pattern is already an ordinary bounded
  result of the `v4`/`v0` arithmetic.
- `H-v29-selection`: the final VGE selects a DMEM-0x60 threshold lane matching
  the sentinel.

Discriminator: reconstruct the four lanes immediately before and after
`vmadh v6,v4,v0`, applying an independent RSP accumulator reference. Endpoint
lanes appearing before saturation select `H-v4-v0-arithmetic`; endpoint lanes
created only by saturation select `H-accumulator-saturation`; a matching
`v29` lane selects `H-v29-selection`.
