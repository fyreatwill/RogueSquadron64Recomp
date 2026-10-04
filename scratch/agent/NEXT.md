# Next work unit: isolate dummy-silent startup without a native predecessor

HYPOTHESIS-ID: m5-dummy-startup-ordering

Session 4071 repeated the retail-gated sequential capture. Retail passed its
positive control and both phase gates; native silent and dummy silent both
reached title 1024 and hangar 512 with no crash/abort. This differs from
session 4069's dummy crash under the same topology, selecting schedule/resource
sensitivity. The next unit removes the preceding native arm to test whether
the dummy process is affected by launch order or native residue.

Competing hypotheses:

- Hdummy-state: dummy-only reproduces the fault, proving the dummy route has a
  deterministic startup dependency independent of a native predecessor.
- Hnative-residue: dummy-only succeeds, so the native predecessor or its cleanup
  changes shared host state relevant to dummy startup.
- Hschedule: dummy-only differs again from the two prior outcomes, leaving the
  route discriminator schedule-sensitive and unevaluable.
- Hcontrol: the retail positive control or phase instrumentation fails in the
  isolation recipe; no port null is interpretable until the control passes.

Discriminating measurement: one build and one retail-gated capture. Launch only
the dummy-silent arm after the retail positive-control marker, with the same
scheduler/task-route breadcrumbs. Record the retail positive-control marker and
both phase gates. Dummy crashing before the gates selects Hdummy-state; dummy
reaching both phases selects Hnative-residue; a changed/unstable result selects
Hschedule; a missing retail control selects Hcontrol and invalidates the arm.

Exact command:

`env RS64_SKIP_NATIVE=1 RS64_S4071_OUT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s4071_m5_dummy_only zsh scratch/agent/run_s4069_m5_sequential_silent.sh`

The driver now supports the `RS64_SKIP_NATIVE=1` dummy-only arm; retain
`ROGUESQ_AUDIO_UCODE=0`,
`ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, all phase
gates, and the retail oracle controls. Use SIGKILL for every game process.
