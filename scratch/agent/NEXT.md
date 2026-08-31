# NEXT work unit — post-sample retail table-entry writers

HYPOTHESIS-ID: m5-output-state-contract-boundary

Session 3467 confirmed the candidate retail table-span writers and their entry
addresses, but `store-field-dump` exposes only the pre-store word. The shared
post-value sampler still sees nonzero retail state pointers, while the
candidate writer/value join remains unevaluable.

Competing hypotheses and discriminating outcomes:

- `H-SourceWriterValue`: the same table entry is selected, but its writer
  stores a different value, selecting the source-table contract edge.
- `H-TablePointerDivergence`: the table pointer/selection differs before the
  load, selecting the producer/selection contract edge.
- `H-ObservationInvalid`: the retail table is invalid; this requires failure
  of both positive controls in the same run.

Work unit: run one independent retail capture retaining the whole-RDRAM and
physical source-watch controls, with `--post-value-watch 1` and
`--post-value-pc 0x80064350,0x80064360,0x80064378,0x800646d8` so the table-span
watch samples post-store words for each candidate writer. Keep the existing
candidate execution watches, load/store rows, phase gates, and source-slot
post-value watch. Join writer address/value to load/store rows by title phase
and per-PC ordinal.

Exact command: use the Session 3467 command, changing the post-value options
to `--post-value-watch 1 --post-value-pc
0x80064350,0x80064360,0x80064378,0x800646d8,0x80064524` and retaining
`--post-value-watch 2 --post-value-pc 0x80064524 --vi-trace`. The base command
is the validated Rice/Start command from Session 3467 with
`--watch-write 0x0:0x800000 --watch-write 0x1b4aa0:0x1b4b24
--watch-write 0x1e8710:0x1e8714 --detail-watch 1`, the four candidate PCs
plus `0x800644a8,0x800644dc,0x80064524`, both title phase gates, and
`--post-value-watch 2 --post-value-pc 0x80064524 --vi-trace`. Keep the run
inside the 35-second title window so the oracle flushes its summaries.

Expected discriminator: same table pointer with a different stored entry value
selects `H-SourceWriterValue`; a different table pointer/selection selects
`H-TablePointerDivergence`; control failure selects `H-ObservationInvalid`.
Do not add port fields or alter audio waits, slots, status handling, consumer
dispatch, clear behavior, or PCM writeback.

Evidence inputs: `scratch/agent/s3464_m5_retail_producer_value/oracle.log` and
`scratch/agent/s3460_m5_source_value_witness_retry/run.log`.
