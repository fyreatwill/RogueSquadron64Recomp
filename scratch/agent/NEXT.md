# Next work unit: M5 non-scalar task-data producer boundary

HYPOTHESIS-ID: m5-task-data-producer-boundary

Session 3753 closed the complete generated scalar-store class. The real and
silent qualified arms both passed `[m5-task-producer-control]`, reached title
and hangar, and recorded 4,096 target-phase rows at physical
`0x171E70..0x171F70`; every value was zero. Retail independently wrote the
same task-data span, including the `0x80090A..0x800911` family. Move upstream
to host pointer writes, RSP DMA, and remaining non-scalar producers. Do not
repeat the scalar census, the nine closed route loads, or alter `0x800078EC`.

Competing hypotheses:

- `H-TaskDataHostProducer`: a native host write populates the task-data span
  in the qualified real arm, but the generated scalar census cannot see it.
- `H-TaskDataRspProducer`: an RSP DMA or other runtime transfer populates the
  span, with the source/task identity joined to the active route.
- `H-TaskDataNonScalarAbsent`: neither host nor RSP/non-scalar producer writes a
  nonzero target value before the zero source DMA; the missing producer is in a
  different runtime boundary.

Discriminator: one build/run must instrument all central host-write APIs and
RSP DMEM-to-RDRAM writes overlapping `0x171E70..0x171F70`, with an independent
same-run positive control for each API, plus the existing real/silent source
join. A nonzero host row selects `H-TaskDataHostProducer`; a nonzero RSP row
selects `H-TaskDataRspProducer`; controls and both phases with no nonzero
host/RSP rows selects `H-TaskDataNonScalarAbsent`. Missing controls or either
target phase is unevaluable.

Ground truth before building: use the existing retail oracle recipe with the
whole-RDRAM control, task-data/source watches, and the known writer-PC family;
do not infer ownership from the port. Add the port diagnostics through a
regeneration-safe script, build once, and run real/silent arms together from
`build/` for 75 seconds. Kill every arm with SIGKILL.
