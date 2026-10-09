# Next work unit (s4367): order exact family writers against task publication

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4366 final Rice capture passed the whole-RDRAM control, both title phase
controls, hangar, and the type-2 task control. Exact writers were live at all
four family addresses. With `--c904-witness`, exact memory histogram indices
are 2–5; index 1 is the task-PC watch. Phase histograms show distinct
title/hangar writer PCs but do not order each store against task publication.

Competing hypotheses:

- H-earlier-producer: the phase-specific task-data families are written by an
  earlier retail producer before the selector/decode handoff.
- H-post-task-transform: the family difference is created after the task data
  is published, by a later consumer or transform.
- H-watch-boundary: the exact watch/task ordinal join remains absent or
  ambiguous, so aggregate histograms say nothing about handoff ordering.

Discriminating measurement: in one bounded Rice retail run, retain each exact
write's phase, writer PC, and monotonic store ordinal, then join it to the
nearest `0x80033FCC` type-2 task ordinal in the same phase/data family. A
writer ordinal before task publication selects H-earlier-producer; only-after
rows select H-post-task-transform; absent or ambiguous joins select
H-watch-boundary.

Build/run: inspect the existing exact-watch and task-join implementation, add
the bounded ordinal instrument in one build if needed, run
`./tools/oracle/build.sh`, then run the Rice oracle for 75 seconds, capturing to
`scratch/agent/soak_results/s4367_selector_writer_task_order.log`. Keep the
whole-RDRAM watch, `--watch-pc 0x80033fcc`, typed task dump, all three
`--pc-phase-log-width` buckets, `--c904-witness`, `--c904-task-join`, and
`--vi-trace`; use exact memory histogram indices 2–5. Reject runs without the
positive control, all three VI origins, or nonzero type-2 rows in every bucket.
