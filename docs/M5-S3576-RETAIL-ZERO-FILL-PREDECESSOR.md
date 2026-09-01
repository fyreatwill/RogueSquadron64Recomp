# M5 s3576 — retail zero-fill predecessor qualification

The planned retail oracle table passed both positive controls: 10,674
whole-RDRAM writes and 674 writes in `0x1797B0..0x179930`. The target phase
`0x006AB400:512` contained 3,165 executions of `0x800078E0`, with observed
predecessors `0x800C825C` (2,260) and `0x800052C4` (866). The presumed
`0x8008F2CC` caller was not watched in this run.

Detailed register rows for the `0x800052C4` edge show `a2` lengths `0x18`,
`0x3C`, `0x208`, `0x4F0`, `0x1008`, and `0x8000`, while the port zero-fill
entry is `dst=0x801797B0`, `fill=0`, `len=0x298`. This selects
`H-ObservedEdgeInput` for the observed `0x800052C4` edge. The exact tuple at
`0x800C825C` and ordering against the first source DMA remain unevaluable;
the capped detail output did not expose that edge's argument rows.

ORIGIN: diagnostic-only retail predecessor/entry qualification. No game
state, output, PCM, task, DMA, or source contents were changed.
