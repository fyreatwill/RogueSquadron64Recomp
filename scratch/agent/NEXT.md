# Next work unit: M5 native task-data value attribution

HYPOTHESIS-ID: m5-task-data-native-value

Session 3755 added a phase-armed native page-fault watch for
`0x171E70..0x171F70`. The paired real/silent run reached title and hangar;
the page positive control fired, and target-range faults were 39/33. PCs
symbolized into generated game functions. The witness does not yet identify
the value stored by the faulting instruction.

Competing hypotheses:

- `H-TaskDataNativeNonzero`: a generated native store writes a nonzero task-data value.
- `H-TaskDataNativeZero`: the observed native stores are legitimate zero-valued stores.
- `H-TaskDataNativeUnrelated`: the fault address overlaps the page, but the
  faulting instruction/value cannot be joined to the task-data field.

Discriminator: one build/run must extend the existing page-fault handler to
decode the faulting store width/source register from the ARM64 context, then
sample the target bytes after the instruction retries. Keep the first-fault
page control, generated scalar census, source-DMA join, and retail oracle
writer attribution in the same measurement. A phase-gated nonzero post-store
sample selects `H-TaskDataNativeNonzero`; zero-only post-store samples select
`H-TaskDataNativeZero`; an undecodable instruction or unmatched post-store
selects `H-TaskDataNativeUnrelated`. Missing controls or either target phase is
unevaluable.

Ground truth already passed this iteration: the retail oracle whole-RDRAM
control and task-data watch fired in title/hangar, with the known
`0x80090A..0x800911` writer family. Do not repeat the retail preflight,
generated scalar census, central host/RSP API census, or closed route-load
list. Build once with the existing macOS arm64 target and run real/silent
arms concurrently from `build/` for 75 seconds, killing both with SIGKILL.
