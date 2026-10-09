# Next work unit (s4368): corroborate family-writer ordering

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4367 final Rice capture passed the whole-RDRAM control, reached both title
buckets and hangar, and retained 1,770 type-2 tasks plus 23,714 exact writes.
The nearest-task ordinal join was before/after = 8047/1, 482/0, 8033/0,
481/0, 798/0, and 5869/3 across the populated buckets, with no missing joins.
This is qualified single-source retail evidence for H-earlier-producer.

Competing hypotheses:

- H-earlier-producer: an independent witness agrees that family writes precede
  the type-2 task publication.
- H-post-task-transform: the independent witness places the family writes only
  after publication.
- H-watch-boundary: the second witness cannot identify the corresponding writer
  or task boundary.

Discriminating measurement: one bounded qualified run using a second evidence
mechanism, not another aggregate histogram, and report the same six phase /
family ordering classes. Before selects H-earlier-producer; only-after selects
H-post-task-transform; absent or contradictory joins select H-watch-boundary.

Build/run: inspect the existing oracle and choose one independent witness for
the same writer/task boundary; build all arms together, then run the Rice route
for 75 seconds. Retain the whole-RDRAM control, `--watch-pc 0x80033fcc`, typed
task dump, all three `--pc-phase-log-width` buckets, `--c904-witness`,
`--c904-task-join`, and `--vi-trace`. Reject runs without the positive control,
all three VI origins, or nonzero type-2 rows in every bucket.
