# Next work unit: M5 residual task-data producer boundary

HYPOTHESIS-ID: m5-task-data-producer-boundary

Session 3754 closed the central host/RSP producer classes. Both qualified arms
passed PI ROM, PI SRAM, zmemcpy, and RSP-DMA controls; neither produced a
phase-gated row overlapping `0x171E70..0x171F70`. The real arm still had 4,096
zero-valued generated scalar rows and reached hangar; retail independently
recorded 50,387 task-data-span writes, including target-phase
`0x80090A..0x800911` writers. Audit remaining arbitrary direct/native and
other non-central writers. Do not repeat the scalar or central API census, the
nine closed route loads, or alter `0x800078EC`.

Competing hypotheses:

- `H-TaskDataDirectNativeProducer`: an arbitrary direct/native writer populates
  the span outside the central host-write APIs and RSP DMA hook.
- `H-TaskDataOtherRuntimeProducer`: another runtime-owned or non-central
  transfer writes the span, with the source/task identity joined to the route.
- `H-TaskDataProducerAbsent`: no remaining port-side producer writes a
  nonzero target value before the zero source DMA.

Discriminator: one build/run must cover the remaining direct/native and other
non-central writers overlapping `0x171E70..0x171F70`, with a positive control
for the new hook/class, plus the existing real/silent source join. A nonzero
direct/native row selects `H-TaskDataDirectNativeProducer`; a nonzero other
runtime row selects `H-TaskDataOtherRuntimeProducer`; controls and both phases
with no nonzero row selects `H-TaskDataProducerAbsent`. Missing controls or
either target phase is unevaluable.

Ground truth before building: use the existing retail oracle recipe with the
whole-RDRAM control, task-data/source watches, and the known writer-PC family;
do not infer ownership from the port. Add the port diagnostics through a
regeneration-safe hook, build once, and run real/silent arms together from
`build/` for 75 seconds. Kill every arm with SIGKILL.
