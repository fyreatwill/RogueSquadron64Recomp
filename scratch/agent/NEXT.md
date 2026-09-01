# NEXT work unit — M5 producer caller comparison

HYPOTHESIS-ID: m5-producer-caller-comparison

Session 3499 selected producer/input divergence: retail and port both reached
the producer and selector controls, but their title-phase
`musyxBuildVoiceCommandList` inputs differed. Compare the caller feeding
`0x80091034` next.

Competing hypotheses and discriminating outcomes:

- `H-CallerParity`: caller PC, arguments, and producer input class match.
- `H-CallerDivergence`: producer is live but caller arguments or input class
  first differ before `0x80091034`.
- `H-CallerObservationFailure`: route control fires but caller rows are absent.

Discriminating measurement: ask the oracle first to watch the retail
predecessor `0x80091330 -> 0x80091034`, with whole-RDRAM and title controls.
Then build once and run the qualified port arm with a phase-gated caller
witness immediately before `jal 0x80091034`. Capture caller PC/RA, `a0..a3`,
and producer input class, plus selector/task/route controls. Matching caller
classes select `H-CallerParity`; live controls with the first differing caller
class select `H-CallerDivergence`; a live route with no caller rows selects
`H-CallerObservationFailure`. No null is interpreted without positive control.

Exact run requirements: use the qualified real-image/LLE/spin-yield/autopilot
route from `build/`, enable `ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_SPIN_YIELD=1`,
`ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`,
`ROGUESQ_AUTOPILOT=1`, `ROGUESQ_LOG_PHASE=1`, `ROGUESQ_LOG_VI_TRANSITION=1`,
`ROGUESQ_LOG_M5_TASK_WRITER=1`, `ROGUESQ_LOG_AUDIO_RETURN=1`, and the caller
plus selector controls. Run the retail preflight first, use a direct-PID
watchdog, capture under `scratch/agent/`, and terminate survivors with
SIGKILL.
