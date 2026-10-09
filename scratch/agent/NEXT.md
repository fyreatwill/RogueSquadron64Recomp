# Next work unit (s4372): locate the selected-word transform/publication boundary

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4371 capture closed the direct selected-word-to-payload comparison with a
second retail evidence line: 102,877 whole-RDRAM writes, all three phase
buckets, 4,483 valid C904/task joins, and 591/591, 601/601, and 344/344
nonzero selected words absent from the first eight payload words by phase.

Competing hypotheses:

- H-transform-before-publication: a later consumer reads or rewrites the
  selected value before the task payload is published.
- H-payload-overwrite: the selected value is initially published, then a later
  writer replaces the first eight payload words before task consumption.
- H-join-alias: the selected row and payload row are still mismatched despite
  valid aggregate joins.

Discriminating measurement: one qualified retail run that adds a phase-gated
watch at the next known intermediate field/writer between C950 and the task
publication, retaining the same C904/C950 row, task ordinal, and payload words.
An intermediate value equal to the selected word then diverging before the
task selects H-transform-before-publication; a payload that briefly equals it
then changes selects H-payload-overwrite; inconsistent task joins selects
H-join-alias. Reject missing positive control, any phase bucket, or fewer than
1,000 valid joins. Do not repeat the already-closed first-eight comparison as
the work unit.

Exact run shape: first identify the existing post-C950 intermediate field
watch in the oracle/runtime docs, then run the Rice retail route for 75 seconds
with `--watch-write 0x0:0x800000`, that field watch, `--watch-pc 0x80033FCC`,
`--pc-task-dump 0x80033FCC --pc-task-type 2 --pc-task-join`,
`--c904-witness --c904-task-join`, explicit phase buckets
`0x00790400:1024`, `0x00790800:1024`, `0x006AB400:512`, and `--vi-trace`.
Do not build unless the missing intermediate instrument requires a source
change; if it is not already available, redesign this work unit before a run.
