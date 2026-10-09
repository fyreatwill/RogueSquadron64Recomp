# Next work unit (s4364): attribute phase-specific task-family writers

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4363 fixed Rice capture passed the whole-RDRAM control and all three phase
controls. At `0x80033FCC`, type-2 task rows were 628/628/429 for origins
`0x00790400`, `0x00790800`, and `0x006AB400`. The selector input stayed
`0x04001000` with words beginning `0x09000419/0x20010FC0`, while task data
pointers and payload families differed by phase. C904/C950 decode witnesses
were phase-labelled and live in hangar only.

Competing hypotheses:

- H-earlier-producer: the phase-specific task-data families are written by an
  earlier retail producer before the selector/decode handoff.
- H-post-task-transform: the family difference is created after the task data
  is published, by a later consumer or transform.
- H-watch-boundary: the candidate data ranges are not the actual source range,
  so a null writer result says nothing.

Discriminating measurement: in one bounded retail run, watch the union
`0x00171000:0x00174000`, retain its first hit and writer-PC histogram, and
phase-gate histograms for all three qualified VI buckets. A phase-specific
writer PC that precedes the task rows selects H-earlier-producer; no writes
after a positive control but valid task-family rows selects H-post-task-transform
only if the watch range is proven to contain the published data; otherwise it
selects H-watch-boundary. Any candidate writer must be checked against the
physical address and phase bucket before promotion.

Build/run: run `./tools/oracle/build.sh`, then from the repo root run the Rice
oracle for 75 seconds, capturing to
`scratch/agent/soak_results/s4364_task_family_writers.log`. Keep the whole-
RDRAM watch, `--watch-pc 0x80033fcc`, typed task dump, all three
`--pc-phase-log-width` buckets, `--c904-witness`, `--c904-task-join`, and
`--vi-trace`; add `--watch-write 0x00171000:0x00174000 --detail-watch 1
--first-watch 1 --pc-hist-watch 1` plus matching `--pc-hist-phase` options.
Reject runs without the whole-RDRAM positive control, all three VI origins, and
nonzero type-2 rows in every bucket.
