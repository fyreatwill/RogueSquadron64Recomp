# NEXT work unit — add port oracle-tuple witness at output/state boundary

HYPOTHESIS-ID: m5-output-state-contract-boundary

Session 3470 attempted the prescribed join. The port title and hangar controls
passed and its ordered table/output rows were present, but the retail
post-value rows have no shared selection or invocation key. The cross-runtime
join was therefore unevaluable. The remaining question is which output/state
field diverges within the port's ordered call chain.

Competing hypotheses and discriminating outcomes:

- `H-OutputStateContract`: port selection is valid, and a downstream field
  diverges between producer and consumer stages.
- `H-ProducerFieldContract`: the source/state tuple diverges before or at the
  first consumer despite the matching table-pointer family.
- `H-PortObservationInvalid`: the new ordered witness or its positive control
  is absent, leaving the boundary unevaluable.

Discriminating measurement: add one phase-scoped port table with
`(pc,s0,s1,source_word,branch_selector,source_byte,branch_state)` at all four
target PCs, and join it by phase and ordinal to the existing port
consumer/output rows. A first divergence after matching producer fields
selects `H-OutputStateContract`; a divergence in the oracle tuple selects
`H-ProducerFieldContract`; missing ordered rows or failed controls select
`H-PortObservationInvalid`.

Work unit: add the regeneration-safe witness, build once, and parse one
phase-gated run. Do not compare sequential animated arms. Do not alter audio
waits, slots, status handling, consumer dispatch, clear behavior, or PCM
writeback.

Exact preparation/build commands:

1. Ask/verify the independent retail tuple schema before changing the port
   witness; retain the Session 3468 artifact as baseline.
2. Add the four-PC tuple witness with the existing schema positive control.
3. Build the configured port and run the title phase from `build/`.
4. Join the new tuple rows to existing output/state rows by phase and ordinal;
   record the first divergent field.

Expected outcomes: a tuple match followed by a downstream divergence selects
`H-OutputStateContract`; an earlier tuple divergence selects
`H-ProducerFieldContract`; missing rows or failed controls select
`H-PortObservationInvalid`. No mitigation or runtime behavior change is
authorized by this unit.

Evidence baseline: `scratch/agent/s3468_m5_retail_post_value/oracle-fixed.log`
and `docs/M5-S3468-RETAIL-POST-VALUE.md`.
