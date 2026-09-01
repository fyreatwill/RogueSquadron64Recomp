# NEXT work unit — M5 selector-load/writer comparison

HYPOTHESIS-ID: m5-selector-load-writer-comparison

Session 3497 qualified the same-build Step 1 pair: both arms reached title
and hangar, and the real image arm produced image-stage/DMA progress. The
next unit is the already-unblocked selector-load/writer comparison, not
another route qualification retry.

Competing hypotheses and discriminating outcomes:

- `H-SelectorParity`: port selector index/source rows match the independent
  retail title route at both selector PCs.
- `H-SelectorDivergence`: both port controls fire, but the first selector
  index/source/value class differs from retail.
- `H-SelectorObservationFailure`: a positive route control fires but one or
  both selector controls/rows are absent, leaving the boundary unevaluable.

Discriminating measurement: build once, run the independent retail task-
dispatch control and the qualified real-image port arm with phase-gated
selector-load/writer rows at `0x80091060` and `0x80091074`, plus the existing
four-PC and route controls. Matching title-origin source/index classes select
`H-SelectorParity`; live controls with a first differing class select
`H-SelectorDivergence`; a missing selector control with a live route control
selects `H-SelectorObservationFailure`. No null is interpreted without the
phase and positive control.

Exact run requirements: use the qualified real-image/LLE/spin-yield route
from `build/`, enable `ROGUESQ_AUDIO_UCODE=1`,
`ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`,
`ROGUESQ_LLE_SOLO=1`, `ROGUESQ_LOG_PHASE=1`,
`ROGUESQ_LOG_VI_TRANSITION=1`, `ROGUESQ_LOG_M5_TASK_WRITER=1`,
`ROGUESQ_LOG_AUDIO_RETURN=1`, and the selector-load/writer controls. Run the
independent retail preflight first, use a direct-PID watchdog, capture under
`scratch/agent/`, and terminate survivors with SIGKILL.
