# Next work unit (s4365): attribute exact phase-specific task-family writers

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4364 fixed Rice capture passed the whole-RDRAM control and all three phase
controls. It recorded 1,786 type-2 task rows and 3,689 C904/task joins. The
union watch `0x00171000:0x00174000` fired, including the four published family
addresses, but mixed initialization/maintenance stores with family traffic and
therefore did not identify a writer for any one published address.

Competing hypotheses:

- H-earlier-producer: the phase-specific task-data families are written by an
  earlier retail producer before the selector/decode handoff.
- H-post-task-transform: the family difference is created after the task data
  is published, by a later consumer or transform.
- H-watch-boundary: the union range is too broad to attribute a published
  family address, so its writer histogram says nothing about the handoff.

Discriminating measurement: in one bounded retail run, watch the four exact
published words separately: `0x00171CE0:0x00171CE4`, `0x00173B20:0x00173B24`,
`0x00171E70:0x00171E74`, and `0x00173CB0:0x00173CB4`, retaining first hits and
writer-PC histograms phase-gated for all three qualified VI buckets. A
phase-specific writer PC that precedes the task rows selects H-earlier-producer;
an exact-address writer only after task publication selects H-post-task-transform;
no exact writes despite valid task-family rows selects H-watch-boundary.

Build/run: run `./tools/oracle/build.sh`, then from the repo root run the Rice
oracle for 75 seconds, capturing to
`scratch/agent/soak_results/s4365_exact_task_family_writers.log`. Keep the
whole-RDRAM watch, `--watch-pc 0x80033fcc`, typed task dump, all three
`--pc-phase-log-width` buckets, `--c904-witness`, `--c904-task-join`, and
`--vi-trace`; add the four exact `--watch-write` ranges, four matching
`--detail-watch`, `--first-watch`, and `--pc-hist-watch` options, plus matching
`--pc-hist-phase` options. Reject runs without the whole-RDRAM positive control,
all three VI origins, and nonzero type-2 rows in every bucket.
