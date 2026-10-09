# Next work unit (s4382): print task publication ordinals and split named writers

HYPOTHESIS-ID: m5-selector-decode-boundary

Competing hypotheses:

- H-post-publication-overwrite: a named writer stores into a published payload
  field after the same task publication.
- H-post-publication-maintenance: named writers occur after publication but
  target maintenance fields outside the task's published field set.
- H-writer-task-join-boundary: the named writer rows are live, but task event
  ordinals are not exposed in the retained task table, so ordering cannot yet
  be measured.

Discriminating measurement: extend the task-dump shutdown row with its saved
`event_ordinal`, then in the same qualified run aggregate ordinal rows by
phase, watch, writer PC, and exact destination against the nearest task. A
named writer row after the same task at a destination in the published field
set selects overwrite; after publication at a destination outside that set
selects maintenance; missing task ordinals or zero named-writer rows selects
the join-boundary hypothesis. Require whole-RDRAM positive control, title and
hangar buckets, at least 1,000 valid type-2 rows, zero ordinal overflow, and
`mismatch=0` for named scalar samples.

Ground-truth preflight: use the independent retail oracle and preserve the
same physical watches and phase schedule. Do not repeat the caller census,
first-eight comparison, or C904 range. Build with `bash tools/oracle/build.sh`
after the task-ordinal instrument change, then run:

    zsh scratch/agent/run_s4381_m5_writer_task_join.sh

The runner is self-contained, uses Rice, emulator mode 1 for the long capture,
and writes to `scratch/agent/s4381_m5_writer_task_join_full/oracle.log`.
