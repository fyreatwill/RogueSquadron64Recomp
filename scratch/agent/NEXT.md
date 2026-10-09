# Next work unit (s4369): compare selector input with published task payload

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4368 fixed capture independently corroborated H-earlier-producer: the
post-store scalar witness reported mismatch=0 for all 16 sampled writer-PC
groups, while the ordinal join placed family writes before the nearest
same-phase type-2 task except four nearest-task boundary outliers. The first
launch omitted the task execution watch and is invalid.

Competing hypotheses:

- H-pre-filter-origin: C904/C950 selector input and selected fields are
  reflected in the first eight task-payload words at publication.
- H-post-task-transform: valid task rows publish phase-specific payloads that
  do not correspond to the C904/C950 input; the meaningful transform is later.
- H-watch-boundary: C904/task joins are absent or phase-incomplete.

Discriminating measurement: one qualified retail run retaining the
whole-RDRAM control, all three VI buckets, `--c904-witness`,
`--c904-task-join`, typed `0x80033FCC` task rows, and the eight-word payload
dump for each joined row. Stable input/selected-to-payload correspondence at
publication selects H-pre-filter-origin; valid unrelated payload families
select H-post-task-transform; missing C904/task coverage selects
H-watch-boundary. Do not promote a single-source relation without a second
evidence line.

Exact run shape: Rice retail route for 75 seconds with the established Start
schedule, `--watch-write 0x0:0x800000`, `--watch-pc 0x80033FCC`,
`--pc-task-dump 0x80033FCC --pc-task-type 2 --pc-task-join`,
`--c904-witness --c904-task-join`, explicit phase buckets
`0x00790400:1024`, `0x00790800:1024`, `0x006AB400:512`, and `--vi-trace`.
Reject missing positive control, any phase bucket, or zero valid C904/task
joins.
