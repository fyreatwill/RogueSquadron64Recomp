# NEXT work unit — M5 pre-call selector-state comparison

HYPOTHESIS-ID: m5-precall-selector-state

Session 3500 selected caller/input divergence: retail's caller at
`0x80091330` was dominated by `a0=0x801772F0, a1=2, a2=1`, while the
qualified port emitted 432 rows with `a0=0x80175960, a1=0, a2=1`.
The next probe must locate the writer or table/slot load that supplies those
caller arguments immediately before the call.

Competing hypotheses and discriminating outcomes:

- `H-PreCallParity`: the caller's preceding loads and source state match
  retail; the divergence is introduced in a later argument transform.
- `H-PreCallState`: the preceding table/slot load or source word differs first
  across retail and port.
- `H-PreCallObservationFailure`: the route controls fire but the new
  pre-call witness has no rows.

Discriminating measurement: ask the oracle first to watch the bounded
predecessor range ending at `0x80091330`, with whole-RDRAM and title controls.
Then build once and run the qualified real-image/LLE/spin-yield/autopilot port
arm with a phase-gated witness at the caller's input-load sequence, capturing
the loaded values, table/slot addresses, and final `a0..a3`. Matching source
classes select `H-PreCallParity`; a first differing source load selects
`H-PreCallState`; live controls with no witness rows select
`H-PreCallObservationFailure`. No null is interpreted without positive
control.

Exact run requirements: use the qualified route from `build/`, enable
`ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_FORCE=1`,
`ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, `ROGUESQ_AUTOPILOT=1`,
`ROGUESQ_LOG_PHASE=1`, `ROGUESQ_LOG_VI_TRANSITION=1`,
`ROGUESQ_LOG_M5_TASK_WRITER=1`, `ROGUESQ_LOG_AUDIO_RETURN=1`, and the caller,
producer, and pre-call controls. Run the retail preflight first, use a
direct-PID watchdog, capture under `scratch/agent/`, and terminate survivors
with SIGKILL.
