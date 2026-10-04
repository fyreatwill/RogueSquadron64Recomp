# Next work unit: isolate the dummy-only startup defect after native success

HYPOTHESIS-ID: m5-dummy-startup-ordering

Session 4070 landed the M3 active-head/sentinel ownership guard and built the
ordinary target. Runtime qualification is unavailable on this host because
`PatchesLib` has no generated target/toolchain. The next applicable M5 unit
remains the route discriminator below. Session 4069 used one retail-gated sequential capture. Native silent reached
title 1024 and hangar 512; dummy silent reproduced the pre-target
`spTaskSchedulerThread+9632` crash with fault `0x400128d47` and guest PC
`0x8000834c`. The next unit keeps the successful native-first ordering but
isolates the dummy arm so its startup/resource state can be compared without a
second port process.

Competing hypotheses:

- Hdummy-state: dummy alone reproduces the same fault, proving the dummy route
  has a deterministic guest scheduler/state defect.
- Hnative-residue: dummy succeeds when launched alone, so native's preceding
  process leaves shared host state that affects dummy.
- Hschedule: dummy termination varies across two same-recipe isolated captures,
  making the current route discriminator schedule-sensitive and unevaluable.
- Hcontrol: the retail positive control or phase instrumentation fails in the
  isolation recipe; no port null is interpretable until the control passes.

Discriminating measurement: one build and one retail-gated capture. Launch the
native silent arm first and SIGKILL it at hangar 512, then launch dummy silent
alone with the same scheduler/task-route breadcrumbs. Record the retail
positive-control marker, native phase markers, and dummy phase/crash signature.
Dummy reproducing the fault selects Hdummy-state; dummy reaching both phases
selects Hnative-residue; a changed/unstable result selects Hschedule; a missing
retail control selects Hcontrol and invalidates the arm result.

Exact command:

`env RS64_S4070_OUT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s4070_m5_dummy_isolated zsh scratch/agent/run_s4069_m5_sequential_silent.sh`

For this work unit, use a copy of the driver with the native-first arm removed
from the second run or a dummy-only driver; retain `ROGUESQ_AUDIO_UCODE=0`,
`ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, all phase
gates, and the retail oracle controls. Use SIGKILL for every game process.
