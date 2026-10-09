# Next work unit (s4388): locate actual hangar task data/output destination

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
VI phase, task, and ordinal controls, plus phase-512 physical watches for the
task `data_ptr` span, `data_ptr+0x100`, and the task output span, each with
writer-PC histograms and bounded phase snapshots. A nonzero/high-volume
hangar writer in the data span selects H-task-data; a live output/other-range
writer with data-span clear-only traffic selects H-task-output; absent,
unsupported, or overflowed target rows select H-watch-gap.

Controls required: whole-RDRAM positive control, title origins
`0x00790400:1024` and `0x00790800:1024`, hangar origin `0x006AB400:512`, at
least 1,000 valid type-2 rows, zero target-watch and ordinal overflow, and
phase snapshots that retain nonzero bytes. Do not interpret ordinal `equal` as
payload equality.

Exact commands:

    bash tools/oracle/build.sh
    create scratch/agent/run_s4388_m5_task_destination_census.sh from the s4387
    runner, replacing the fixed range-2 watch with the task data/output spans
    discovered from the retained hangar task rows
    bash scratch/agent/run_s4388_m5_task_destination_census.sh

Summarize only bounded `rg`/`sed` windows from the oracle log.
