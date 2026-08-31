# NEXT work unit — join port and retail source-writer values

HYPOTHESIS-ID: m5-output-state-contract-boundary

Session 3462 qualified the missing independent retail table: 1,294 ordered
title rows at origin `0x00790400`, with 978 zero rows at `0x800644B0` and 316
rows at `0x80064524` carrying `0x80194EA0`, `0x801B4F00`, or `0x801B5E70`.
The whole-RDRAM and physical source-watch controls both fired. The existing
qualified port title sequence remains 1,024 rows (768/256), all zero.

Competing hypotheses and discriminating outcomes:

- `H-PortRetailJoin`: the qualified port and retail rows join, closing this
  source boundary.
- `H-FirstValueDivergence`: the first joined value differs, selecting the
  missing writer/value contract edge.
- `H-FirstWriterDivergence`: the first joined writer differs, selecting the
  missing route/producer edge.

Run the existing qualified LLE/spin-yield port source-writer capture and join
its ordered `(title phase, writer PC, post-store value)` rows to
`scratch/agent/s3462_m5_retail_ordered_source/oracle.log` by phase, PC, and
ordinal. An exact sequence selects `H-PortRetailJoin`; a matching writer with
a different value selects `H-FirstValueDivergence`; a different writer
selects `H-FirstWriterDivergence`; missing ordered port rows are unevaluable.
Keep the same positive control and do not alter audio waits, slots, dispatch,
clear behavior, or PCM writeback.
