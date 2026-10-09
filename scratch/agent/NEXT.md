# Next work unit (s4362): repair hangar C904/task payload join

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4361 capture qualified whole-RDRAM, title, and hangar coverage. Its new
payload field was live in 1,786 type-2 task rows, and title joins showed a
constant C904/C950 input with phase/data-block-specific payload words. The
summary retained no hangar C904-task rows even though hangar task rows were
live, so the cross-phase discriminator is not yet qualified.

Competing hypotheses:

- H-selector-multiplex: the hangar task payload is a distinct family selected
  before or at the task handoff, as the two title-origin payload families
  suggest.
- H-consumer-transform: title and hangar share the joined payload/input and a
  later consumer transform creates the observed divergence.
- H-pre-filter-origin: a repaired hangar join exposes disagreement already in
  the payload fields relative to its C904/C950 selector input.

Discriminating measurement: fix the join ordering/key so a C904/C950 witness
at `0x8009C904`/`0x8009C950` can join the latest type-2 task row at
`0x80033FCC` in the `0x006AB400` bucket, then print/count the existing
eight-word `data_ptr` payload for title and hangar. A valid hangar join with a
distinct payload family selects H-selector-multiplex; a shared payload followed
by later-only divergence selects H-consumer-transform; disagreement against
the joined selector input selects H-pre-filter-origin. If the join remains
empty, the result is an instrument-boundary finding, not a hypothesis result.

Build/run: edit `tools/oracle/rs64_oracle.c`, run `./tools/oracle/build.sh`,
then from `build/` repeat the verified Rice command used for s4361 for 75 s,
capturing to `scratch/agent/soak_results/s4362_hangar_payload_join.log`. Keep
`--watch-write 0x0:0x800000`, `--watch-pc 0x80033fcc`,
`--pc-task-dump 0x80033fcc`, all three
`--pc-phase-log-width 0x00790400:1024`, `0x00790800:1024`,
`0x006AB400:512`, `--c904-witness`, `--c904-task-join`, and `--vi-trace`.
Reject runs without the whole-RDRAM positive control and all three phase
origins.
