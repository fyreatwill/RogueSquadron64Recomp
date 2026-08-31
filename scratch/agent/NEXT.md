# NEXT work unit — identify the producer feeding the shared source writer

HYPOTHESIS-ID: m5-output-state-contract-boundary

Session 3463 joined the qualified sequences. All 768 comparable
`0x800644B0` rows match at zero. At shared writer `0x80064524`, the first
comparable row is port zero versus retail `0x801B4F00`; writer PC matches.

Competing hypotheses and discriminating outcomes:

- `H-RetailProducerMatched`: the producer/value feeding `0x80064524` matches
  across runtimes, closing this value edge.
- `H-ProducerValueDivergence`: producer or value differs, selecting the next
  contract edge.
- `H-RetailObservationInvalid`: the independent writer/value observation is
  invalid; this requires failure of both positive controls in the same run.

Work unit: obtain an independent retail producer/value table for the store at
`0x80064524`, retaining the whole-RDRAM and physical source-watch controls.
Use the existing oracle build and a single run, with ordered post-store rows
and title phase gating. Then join it to the existing qualified port rows by
title phase and per-PC ordinal.

Expected discriminator: matching producer/value rows select
`H-RetailProducerMatched`; a first producer or value difference selects
`H-ProducerValueDivergence`; a control failure selects
`H-RetailObservationInvalid`. Do not add port fields or alter audio waits,
slots, dispatch, clear behavior, or PCM writeback.

Evidence inputs: `scratch/agent/s3461_m5_source_value_join/run.log` and
`scratch/agent/s3462_m5_retail_ordered_source/oracle.log`.
