# Next work unit: M5 qualified-route predecessor/handoff census

HYPOTHESIS-ID: m5-qualified-route-predecessor-handoff

Run one batched, phase-gated capture joining the first real-audio route edge
after the shared `rs_strncpy`/texture-LUT setup to its task/RSP handoff and
qualified source-DMA row. Retain the oracle whole-RDRAM control, both source
watches, both VI snapshots, exact source-span stores, and real/silent controls.
Do not change port behavior or suppress the legitimate `0x800078EC` zero fill.
Reuse `scratch/agent/run_s3737_m5_retail_writer_join.sh`; batch all route-edge
fields into one build/run.

Competing hypotheses:

- `H-RouteHandoffValueAbsent`: the real-audio route enters the handoff with
  zero/uninitialized source/value state.
- `H-RouteHandoffDropsValue`: a nonzero setup/DMEM value becomes zero between
  the route predecessor and the task/RSP handoff.
- `H-RouteHandoffAfterClear`: the qualified route receives a nonzero value and
  a later legitimate clear precedes the zero source DMA.

Discriminator: compare the first route predecessor value, handoff value, and
qualified source-DMA payload in the same title/hangar phase. Zero at both
predecessor and handoff selects `H-RouteHandoffValueAbsent`; nonzero
predecessor becoming zero at handoff selects `H-RouteHandoffDropsValue`; a
nonzero handoff followed by the known legitimate clear selects
`H-RouteHandoffAfterClear`. Missing oracle control or either target phase is
unevaluable.

Ground truth must be checked before building: retain the existing oracle
whole-RDRAM watch, both phase watches, and retail writer-PC options. A
positive-control miss, absent phase, or absent real-audio source route makes
the result unevaluable.
