# Next work unit: M5 route-value producer census

HYPOTHESIS-ID: m5-route-value-producer-census

Run one batched, phase-gated capture tracing the earlier writer/state
transition that supplies the zero `source_word/source_byte/branch_state` seen
at `0x80019CD8` and the zero value fields at the `0x8000C628` handoff. Retain
the oracle whole-RDRAM control, both source watches, both VI snapshots, exact
source-span stores, route candidate/prepare/handoff logs, and real/silent
controls. Do not change port behavior or suppress the legitimate
`0x800078EC` zero fill. Extend the existing script/instrument in one build
and one run; use the oracle before building.

Competing hypotheses:

- `H-EarlierWriterAbsent`: the earlier route-state writer never publishes a
  nonzero source/value state before the qualified route.
- `H-EarlierWriterClears`: an earlier legitimate writer clears a previously
  nonzero route value before the qualified route.
- `H-RouteStateNotSource`: the observed route fields are control metadata and
  the missing source payload is produced by a separate unjoined state/object.

Discriminator: join the first earlier writer and its value to the first
route-preparation row, handoff row, and qualified source-DMA row in each
target phase. No earlier nonzero writer plus zero route state selects
`H-EarlierWriterAbsent`; a nonzero earlier writer followed by zero route state
selects `H-EarlierWriterClears`; matching route metadata with no source join
selects `H-RouteStateNotSource`. Missing oracle control or either target phase
is unevaluable.

Ground truth must be checked before building: retain the existing oracle
whole-RDRAM watch, both phase watches, and retail writer-PC options. A
positive-control miss, absent phase, or absent real-audio source route makes
the result unevaluable.
