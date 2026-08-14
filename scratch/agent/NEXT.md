# NEXT work unit (s1017)

HYPOTHESIS-ID: m4-zero-shade-accumulator-origin

Run one corrected, phase-gated M4 accumulator capture. Gate on reachable
1024, keep capturing after the width changes, and send the documented menu
schedule relative to 1024; do not gate directly on 512 because that starts
the key worker too late to cause the transition.

Competing hypotheses and discriminating measurement:

- `H-512-reached`: the 1024-relative schedule transitions to 512 and both the
  M4 target and VMADH positive control fire.
- `H-schedule-still-wrong`: Start is positive but the schedule leaves 1024
  without reaching 512; the input/state prerequisite remains wrong.
- `H-probe-control-failure`: the corrected run fails to arm the 1024 gate or
  its independent control, making the capture invalid rather than M4 evidence.

The discriminator is one same-run table: phase timeline, key records, M4
accumulator rows, and VMADH positive-control rows. A 512 transition plus both
controls makes the M4 rows evaluable; no 512 transition keeps the M4 question
open; missing 1024/control records invalidates the run.

Exact starting commands:

Exact command (from repo root; build only after the 1024 control is positive):

`env ROGUESQ_LOG_INPUT=1 ROGUESQ_LOG_M4_ACCUM=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start" zsh tools/probe.sh scratch/agent/probe_results/m4_accum_1024 300 2`
