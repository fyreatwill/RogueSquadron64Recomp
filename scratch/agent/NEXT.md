# NEXT work unit — identify the table-entry producer feeding the shared writer

HYPOTHESIS-ID: m5-output-state-contract-boundary

Session 3464 showed that the retail producer callsite `0x800644A8` is active,
but the intervening table walk loads the nonzero `s0` values observed at
`0x80064524`. The first joined store row remains port zero versus retail
`0x801B4F00`; all 768 comparable `0x800644B0` rows match at zero.

Competing hypotheses and discriminating outcomes:

- `H-TableLoadMatched`: retail and port load the same table entry at
  `0x800644DC`, closing this edge at the store's input.
- `H-TableEntryDivergence`: the loaded table entry or its producer differs,
  selecting the source-table contract edge.
- `H-ObservationInvalid`: the retail table is invalid; this requires failure
  of both positive controls in the same run.

Work unit: run one independent retail capture retaining the whole-RDRAM and
physical source-watch controls, with title-gated ordered execution rows at
`0x800644DC` (the `lw s0,0(v1)` table-entry load), `0x800644A8`, and
`0x80064524`, plus post-store values. Join by title phase and per-PC ordinal
to the existing port source-writer rows.

Expected discriminator: matching `s0`/table-entry rows select
`H-TableLoadMatched`; a first table-entry or producer difference selects
`H-TableEntryDivergence`; control failure selects `H-ObservationInvalid`.
Do not add port fields or alter audio waits, slots, status handling, consumer
dispatch, clear behavior, or PCM writeback.

Evidence inputs: `scratch/agent/s3464_m5_retail_producer_value/oracle.log` and
`scratch/agent/s3460_m5_source_value_witness_retry/run.log`.
