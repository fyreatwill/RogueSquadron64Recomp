# Next work unit (s4389): split exact hangar task data spans

HYPOTHESIS-ID: m5-selector-decode-boundary

Competing hypotheses:

- H-task-data: the semantic hangar payload is in the task's `data_ptr` span
  (`0x80171E70` plus the task's `data_size`/nearby `+0x100` field), not the
  stale cleared range `0x80178C80`.
- H-task-output: the semantic payload is in the task output or another
  phase-specific destination, while `data_ptr` is only a selector/input.
- H-watch-gap: the bounded task-field or physical watch cannot retain the
  relevant hangar stores.

Discriminating measurement: one retail-oracle run with the same whole-RDRAM,
VI phase, task, and ordinal controls, plus exact physical watches for both
observed hangar data spans (`0x171E70:0x173290` and
`0x173CB0:0x1750D0`), their exact `+0x100` four-byte fields, and the null
output span. A nonzero/high-volume writer inside the task span, with no
output writers, selects H-task-data; a live output/other-range writer with
task spans clear selects H-task-output; absent, unsupported, or overflowed
target rows select H-watch-gap.

Controls required: whole-RDRAM positive control, title origins
`0x00790400:1024` and `0x00790800:1024`, hangar origin `0x006AB400:512`, at
least 1,000 valid type-2 rows, zero target-watch and ordinal overflow, and
phase snapshots that retain nonzero bytes. Do not interpret ordinal `equal` as
payload equality.

Exact commands:

    bash tools/oracle/build.sh
    bash tools/oracle/build.sh
    create scratch/agent/run_s4389_m5_exact_task_spans.sh from the s4388
    runner, using separate exact watches for both data spans and both fields
    bash scratch/agent/run_s4389_m5_exact_task_spans.sh

Summarize only bounded `rg`/`sed` windows from the oracle log.
