# Next work unit: M5 native task-data value attribution — stable target-only retry

HYPOTHESIS-ID: m5-task-data-native-value

Session 3756 added ARM64 source-register/value decoding to the phase-armed
watch for `0x171E70..0x171F70`. The page positive control fired, but the
paired run had no target-phase attribution rows: real later crashed in
`musyxBuildVoiceCommandList`, while silent crashed in `spTaskSchedulerThread`
before target gating. This is unevaluable, not a zero result.

Competing hypotheses:

- `H-TaskDataNativeNonzero`: a generated native store writes a nonzero task-data value.
- `H-TaskDataNativeZero`: the observed native stores are legitimate zero-valued stores.
- `H-TaskDataNativeUnrelated`: the fault address overlaps the page, but the faulting instruction/value cannot be joined to the task-data field.
- `H-TaskDataNativeRunUnstable`: the page watch perturbs or coincides with a crash before target attribution.

Discriminator: patch the existing handler so instruction decoding runs only for
phase-gated exact faults, retain the first-fault page positive control, and
sample target bytes after the instruction retries. A phase-gated nonzero
post-store sample selects `H-TaskDataNativeNonzero`; zero-only samples select
`H-TaskDataNativeZero`; an undecodable or unmatched target fault selects
`H-TaskDataNativeUnrelated`; another pre-phase crash selects
`H-TaskDataNativeRunUnstable`. Missing controls or either target phase is
unevaluable.

Ground truth already passed in session 3755: the retail oracle whole-RDRAM
control and task-data watch fired in title/hangar, with the known
`0x80090A..0x800911` writer family. Do not repeat the retail preflight,
generated scalar census, central host/RSP API census, or closed route-load
list. Build once with `cmake --build build --config Debug --target RogueSquadron64Recomp`,
then run the documented LLE/spin-yield/autopilot real/silent pair from
`build/` for 75 seconds with `ROGUESQ_LOG_M5_TASK_WRITE_FAULT=1`, killing both
with SIGKILL. Expect a target-phase decoded value, target-phase zero rows,
explicit run-unstable evidence, or an unevaluable control/phase.
