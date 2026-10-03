# Next work unit: M5 non-scalar/host exact route-field ownership

HYPOTHESIS-ID: m5-nonscalar-exact-route-field-ownership

Run one batched, phase-gated capture for exact route fields `0x80128C92` and
`0x80128CD0..0x80128CD4`, covering DMA/host-side and non-literal-address
writers, and join them to route prepare/handoff and source-DMA rows. Retain
the oracle whole-RDRAM control, exact physical watches, title route-PC watch,
both VI snapshots, and real/silent controls. Do not alter `0x800078EC`.
Ask the oracle before building for the exact-field watches and writer-PC
histogram; then make one build and one paired run, with a real-alone rerun
only if the real arm fails to reach both target phases.

Competing hypotheses:

- `H-ExactFieldUnwritten`: the exact fields have no writer before the qualified route, so the zero route state is an absent producer.
- `H-ExactFieldNonScalar`: a byte-lane, doubleword, DMA, or host-side write supplies the fields outside the generated scalar census.
- `H-RouteStateNotSource`: the exact fields are control metadata and the image source is produced by a separate unjoined object.

Discriminator: a non-scalar/host exact-field writer with nonzero payload before
a zero route row selects `H-ExactFieldNonScalar`; no exact-field writer with a
valid source-DMA join selects `H-ExactFieldUnwritten`; matching route metadata
with no exact-field/source join selects `H-RouteStateNotSource`.
Missing oracle control, positive port control, or either port target phase is
unevaluable.

Ground truth must be checked before building: use the oracle whole-RDRAM watch,
the exact physical route-field range, title route-PC watch, and writer-PC
histogram. A positive-control miss, absent title/hangar phase, or absent
real-audio source route makes the result unevaluable.
