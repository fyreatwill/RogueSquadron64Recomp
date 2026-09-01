# NEXT work unit — M5 Step 1 same-build audio qualification

HYPOTHESIS-ID: m5-audio-step1-contract-qualification

Session 3496's fresh real-audio route crashed before title at guest PC
`0x8000B650`, so selector comparison is parked. The next unit is M5 plan
Step 1, not another unchanged real-audio retry.

Competing hypotheses and discriminating outcomes:

- `H-AudioDegeneracy`: the silent arm lacks the image's task/DMEM/DMA/service
  progress, while the real image completes and shows downstream audio rows.
- `H-ImageRouteFailure`: the real image arm fails before target phase while
  the silent arm remains qualified; this keeps the missing contract edge
  unevaluable and points to the image route itself.
- `H-SharedRuntimeFailure`: both arms fail or stop before their controls,
  separating a shared scheduler/runtime problem from image-specific work.

Discriminating measurement: build once, then run the silent control and the
default real image arm from the same build with phase-gated task dispatch/exit,
DMEM/DMA, SP completion, service/slot, PCM, MORT, and title/hangar controls.
Require positive controls in each arm. Image completion plus downstream
progress selects `H-AudioDegeneracy`; silent qualification plus image-only
pre-title failure selects `H-ImageRouteFailure`; matched failure selects
`H-SharedRuntimeFailure`. No null is interpreted without its arm's phase and
positive control.

Exact run requirements: use the validated AUTOPILOT/phase-gated recipe from
the M5 plan, launch both arms from `build/`, keep `ROGUESQ_AUDIO_UCODE=0` as
the silent arm and the default image arm as the other arm, enable
`ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`,
`ROGUESQ_LLE_SOLO=1`, `ROGUESQ_LOG_PHASE=1`,
`ROGUESQ_LOG_VI_TRANSITION=1`, `ROGUESQ_LOG_M5_TASK_WRITER=1`, and
`ROGUESQ_LOG_AUDIO_RETURN=1`. Run arms concurrently where the recipe allows,
use a direct-PID watchdog, capture under `scratch/agent/`, and terminate
survivors with SIGKILL.
