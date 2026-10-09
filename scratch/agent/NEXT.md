# Next work unit (s4373): phase-key the selected-word transform/publication join

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4372 fixed capture passed controls and produced 29,672 C904/task matches,
but the generic boundary-PC field table retained only hangar rows. The title
task/C904 joins were live, so the missing title intermediate rows are an
instrument boundary, not evidence about the transform.

Competing hypotheses:

- H-transform-before-publication: C950's selected word is consumed by the
  decode path and differs before the DC38 publication store.
- H-payload-overwrite: a publication-stage value first equals the selected
  word, then a later writer changes it before task consumption.
- H-phase-instrument-gap: title intermediate rows are absent despite live
  title C904/task joins, so the capture cannot classify either value path.

Discriminating measurement: one oracle build/run with an explicit phase-keyed
join retaining C950/C954's selected word, D78C/D790's cursor transition, and
DC38's publication source by the same phase/task ordinal. An intermediate
value equal to the selected word then diverging before publication selects
H-transform-before-publication; a publication value that briefly equals it
then changes selects H-payload-overwrite; missing title rows with live title
joins selects H-phase-instrument-gap. Reject missing positive control, any
phase bucket, or fewer than 1,000 valid joins.

Exact run shape: implement the phase-keyed oracle join at C950/C954,
D78C/D790, and DC38, then build the oracle and run the Rice retail route for
75 seconds with `--watch-write 0x0:0x800000`, `--watch-pc 0x80033FCC`,
`--pc-task-dump 0x80033FCC --pc-task-type 2 --pc-task-join`,
`--c904-witness --c904-task-join`, explicit phase buckets
`0x00790400:1024`, `0x00790800:1024`, `0x006AB400:512`, and `--vi-trace`.
Do not repeat the closed first-eight payload comparison.
