# NEXT work unit (classify ordinary versus synthetic late range records)

HYPOTHESIS-ID: m3-e9-command-boundary

Perform one bounded telemetry-only probe using s838's late records. Add a
distinct marker/counter for synthetic FULL_SYNC submissions and for ordinary
`rs64_dpc_record_submit`/consumer pairs, retain the existing positive controls
and phase gates, build all arms together, and run once. Do not change behavior
or add a mitigation.

Competing hypotheses and discriminator:

- H-ordinary-disjoint: ordinary accepted submissions remain disjoint from the
  parser call ranges.
- H-synthetic-stale-label: disjoint rows are synthetic submissions carrying
  the previous serial/range label; ordinary pairs remain exact.
- H-parser-record-loss: ordinary parser call ranges are present, but command
  telemetry omits their contents.

Discriminator: synthetic markers covering the disjoint rows select
H-synthetic-stale-label; exact ordinary pairs with missing command records
select H-parser-record-loss; disjoint ordinary pairs select H-ordinary-disjoint.
