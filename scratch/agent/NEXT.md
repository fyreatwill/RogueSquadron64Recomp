# NEXT work unit — trace the upstream selector/table producer

HYPOTHESIS-ID: m5-task-field-writer

Session 3489 selected `H-WriterInputDivergence`: retail supplied only
`0x80171CE0`, while the silent port supplied that value plus `0x80173B20` and
`0x8018DD30` at the common writer. The source-family key had qualified overlap,
so the next work unit is upstream attribution, not another join-key design.

Competing hypotheses and discriminating outcomes:

- `H-UpstreamProducerDivergence`: the selector/table producer supplies a
  route-exclusive source value before `0x80091074`.
- `H-SelectorLoadDivergence`: producer inputs match, but the load/selection
  operation changes the source before the writer.
- `H-JoinInsufficient`: both controls fire but the producer key has no
  qualified overlap, requiring a redesigned key.

Discriminating measurement: add one batched witness at the preceding selector
load/table-read boundary, retaining the existing controls, and join retail and
port rows by title origin, source family, selector input, and operand class.
A route-exclusive producer value selects `H-UpstreamProducerDivergence`; equal
producer inputs with differing writer values selects `H-SelectorLoadDivergence`;
no qualified overlap selects `H-JoinInsufficient`.

Ground truth before building: use the independent retail oracle to watch the
preceding selector load/table-read boundary and require its whole-RDRAM
positive control in the same run. Then batch both arms in one build/run
recipe; do not compare sequential animation ordinals.
