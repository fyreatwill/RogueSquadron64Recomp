# Session 5280 M4 port-side mid-task accumulator capture

The Debug build completed successfully. A first capture reached title but
spent the mid-task cap before hangar; it is not used for the discriminator.
The corrected capture set `ROGUESQ_M4_PHASE_FROM=5` and a fresh target cap,
and reached title `0x00790400`/1024 at 49.8s and hangar
`0x006AB400`/512 at 58.0s. It armed the M4 mid-task and task-end probes in
one run and terminated with SIGKILL after capture.

Controls:

- The phase marker reached the qualified 512-wide hangar phase.
- The build was from the current Debug tree.
- No `[CRASH]` marker occurred.
- The task-end probe emitted 352 phase-5 rows.

Results:

- The port emitted 2,000 bounded phase-5 mid-task rows: 505 stage-10,
  505 stage-11, 505 stage-12, and 485 stage-13 rows.
- 18 of those rows contained an `0x8000` component in a sampled VACC lane.
  The positive examples include `accl=8000`; this is a real transient
  mid-task observation, not a task-end decode.
- None of the 352 phase-5 task-end rows had `sat8000`.
- The mid-task cap concentrated on one task because a single task invokes the
  four stages repeatedly. Therefore this run does not establish the retail
  per-task prevalence or timing distribution.

The port can create transient `0x8000` accumulator state and clears it by
task end, matching the qualitative retail pattern from S5279. This is
single-source port evidence. It selects the transient-state branch over a
claim that the port never creates `0x8000`, but does not yet distinguish
retail-equivalent timing from a port-specific transient lifetime. No
mitigation is authorized.

Capture: `scratch/agent/m4_port_capture_5280_fixed.log`.
