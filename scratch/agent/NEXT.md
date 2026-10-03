# Next work unit: M5 exact route-field ownership

HYPOTHESIS-ID: m5-exact-route-field-ownership

Run one batched, phase-gated capture that traces the exact route-object fields
used by the qualified route (`a0=0x80128C70`, fields `+0x60` and `+0x22`) and
joins every scalar and non-scalar store to the route prepare/handoff rows and
source-DMA row. Retain the oracle whole-RDRAM control, title route-PC watch,
both VI snapshots, route candidate/prepare/handoff logs, and real/silent
controls. Do not change port behavior or suppress the legitimate
`0x800078EC` zero fill. Ask the oracle before building for an exact-field
write watch and its writer-PC histogram; then make one build and one paired
run.

Competing hypotheses:

- `H-ExactFieldUnwritten`: the exact fields have no writer before the qualified
  route, so the zero route state is an absent producer.
- `H-ExactFieldNonScalar`: a byte-lane, doubleword, DMA, or host-side write
  supplies the fields outside the scalar census.
- `H-RouteStateNotSource`: the exact fields are control metadata and the image
  source is produced by a separate unjoined object.

Discriminator: an exact-field writer with nonzero payload before a zero route
row selects `H-ExactFieldNonScalar` (or proves a clear); no exact-field writer
with a valid source-DMA join selects `H-ExactFieldUnwritten`; matching route
metadata with no exact-field/source join selects `H-RouteStateNotSource`.
Missing oracle control, positive port control, or either port target phase is
unevaluable.

Ground truth must be checked before building: use the oracle whole-RDRAM watch,
the exact physical route-field range, title route-PC watch, and writer-PC
histogram. A positive-control miss, absent title/hangar phase, or absent
real-audio source route makes the result unevaluable.
