# Next work unit (s4383): extend the writer join through hangar

HYPOTHESIS-ID: m5-selector-decode-boundary

Competing hypotheses:

- H-hangar-route-late: the qualified 50-second run reached hangar tasks too
  late to retain payload-range writes; a longer same-route capture will make
  the named writers live there.
- H-hangar-maintenance-or-other-range: hangar tasks are live, but the named
  writers do not target either watched payload range in hangar.
- H-writer-task-join-boundary: task ordinals or writer rows remain absent even
  with longer hangar coverage.

Discriminating measurement: rerun the same oracle with `--secs 75` and
aggregate hangar rows by writer PC, exact destination, and nearest task. Hangar
named-writer rows with after-publication stores select a live hangar writer
path; zero target-range writes with live task ordinals selects the other-range
or maintenance hypothesis; missing task ordinals selects the join boundary.
Require whole-RDRAM positive control, all three buckets, at least 1,000 valid
type-2 rows, zero ordinal overflow, and `mismatch=0` for named scalar samples.

Ground-truth preflight: use the independent retail oracle and preserve the
same physical watches and phase schedule. Do not repeat the caller census,
first-eight comparison, or C904 range. Build with `bash tools/oracle/build.sh`
after the task-ordinal instrument change, then run:

    sed 's/--secs 50/--secs 75/' scratch/agent/run_s4381_m5_writer_task_join.sh > scratch/agent/run_s4383_m5_writer_task_join.sh
    zsh scratch/agent/run_s4383_m5_writer_task_join.sh

The runner is self-contained, uses Rice, emulator mode 1 for the long capture,
and writes to `scratch/agent/s4381_m5_writer_task_join_full/oracle.log`.
