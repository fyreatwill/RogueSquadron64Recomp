# NEXT work unit (s2283) — A1 VI publisher/cadence matrix

HYPOTHESIS-ID: m5-a1-vi-publisher-cadence

## Work unit

Run one same-build, phase-gated four-arm matrix using the existing VI context and
parity-scheduler diagnostics. Keep all runtime defaults unchanged. The arms are:
"control" with no VI behavior arm, "alternate-field" with
ROGUESQ_VI_ALTERNATE_FIELDS=1, "current-reg-screen" with
ROGUESQ_VI_FIELD_FROM_CURRENT_REG=1 ROGUESQ_VI_CURRENT_REG_TOGGLE_BEFORE_SCREEN=1,
and "retrace-parity" with
ROGUESQ_VI_FIELD_FROM_CURRENT_REG=1 ROGUESQ_VI_CURRENT_REG_FROM_TOTAL_VIS=1.
Run the four port arms and one retail oracle in the same iteration. Stop each
port arm only after it has supplied the positive all-width VI-context control
and either the first target origin 0x00696100 or the second-origin target
0x00696600; retain 15 seconds after the first second-origin row. Kill every
remaining process with SIGKILL.

## Competing hypotheses and discriminating measurement

- H-CallbackPublisher: the natural publisher is callback/field cadence. The
  control or alternate-field arm supplies the only stable 0x00696600 rows, and
  their selected field tracks callback ordinal parity rather than total_vis & 1.
- H-TotalViPublisher: the natural publisher is total-VI/retrace parity. Only
  retrace-parity supplies the second-origin rows, with selected_field equal to
  total_vis & 1 and stable origin/field mapping.
- H-ScreenTiming: the missing boundary is the screen-enqueue timing edge. Only
  current-reg-screen changes second-origin reachability; its rows differ from
  retrace-parity at equal callback ordinal and show the decisive
  skipped_vi/delta relationship.
- H-NoPublisher: none of the arms reaches the second-origin target after
  passing its positive control, so the current host publisher/cadence remains
  unobserved and the next probe must move to the host VI callback/queue boundary.

The single discriminating table is keyed by
arm, callback_ordinal, total_vis, delta, callback_parity, total_parity,
selected_field, current_line, committed_origin, skipped_vi. Require every arm
to have its [vi-context-port-control] and [vi-parity-scheduler-control]
positive rows before interpreting a second-origin null. Select the publisher
only when one arm's second-origin rows are reproducible and its parity/timing
relation predicts the other arms' rows; otherwise retain H-NoPublisher.
The same-run retail oracle must pass whole-RDRAM >=10,000 writes and show both
target 640 origins under the driven Rice route.

## Exact commands

1. Create scratch/agent/run_s2283_m5_vi_publisher_matrix.sh with apply_patch.
   Base its process/watchdog structure on
   scratch/agent/run_s2205_vi_toggle_stability_ab.sh. Use one oracle command
   with --watch-write 0x0:0x800000 --vi-trace,
   --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib, and
   the established eleven-Start --press schedule. Each port arm must set
   ROGUESQ_AUDIO_UCODE=0, ROGUESQ_SPIN_YIELD=1,
   ROGUESQ_LLE_UNGATED=1, ROGUESQ_LLE_SOLO=1,
   ROGUESQ_LOG_PHASE=1, ROGUESQ_LOG_VI_CONTEXT_PORT=1,
   ROGUESQ_LOG_VI_PARITY_SCHEDULER=1, and
   ROGUESQ_LOG_VI_TRANSITION=1, plus its one behavior-arm setting.
2. Run from the repository root:
   zsh scratch/agent/run_s2283_m5_vi_publisher_matrix.sh s2283_m5_vi_publisher_matrix
3. Summarize, with bounded grep/tail only, the retail positive control and
   each arm's control rows, first/second-origin rows, table tuples, terminal
   phase, and crash/timeout. Do not change any VI behavior default or infer a
   publisher from an arm that lacks its positive controls.
