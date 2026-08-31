# NEXT work unit — attribute the retail source-table entry writer

HYPOTHESIS-ID: m5-output-state-contract-boundary

Session 3465 showed that retail's intervening load at `0x800644DC` feeds
nonzero values such as `0x801B4F00` into `0x80064524`, while the qualified port
store remains zero. The load's `v1` table-entry addresses are now observed;
the instruction that writes those entries is not.

Competing hypotheses and discriminating outcomes:

- `H-SourceWriterValue`: the same table entry is selected, but its writer
  stores a different value, selecting the source-table contract edge.
- `H-TablePointerDivergence`: the table pointer/selection differs before the
  load, selecting the producer/selection contract edge.
- `H-ObservationInvalid`: the retail table is invalid; this requires failure
  of both positive controls in the same run.

Work unit: run one independent retail capture retaining the whole-RDRAM and
physical source-watch controls, with a title-gated watch on the candidate
source-table entry writer discovered from the table walk, plus the existing
`0x800644DC`, `0x800644A8`, and `0x80064524` execution rows and post-store
values. Join by title phase and per-PC ordinal.

Exact commands: first use `rg -n "801B4AA0|801B4AA8|801B4B20|800644DC"
tools syms RecompiledFuncs` to identify the candidate store instruction; then
run `tools/oracle/build/rs64_oracle` with `--watch-write 0x0:0x800000
--watch-write 0x001e8710:0x001e8714`, `--watch-pc` for the candidate plus
`0x800644A8,0x800644DC,0x80064524`, `--pc-phase-log-width
0x00790400:1024 --pc-phase-log-width 0x00790800:1024`, and
`--post-value-watch 1 --post-value-pc 0x80064524 --vi-trace` using the
validated Rice/Start schedule.

Expected discriminator: same table pointer with a different stored entry value
selects `H-SourceWriterValue`; a different table pointer/selection selects
`H-TablePointerDivergence`; control failure selects `H-ObservationInvalid`.
Do not add port fields or alter audio waits, slots, status handling, consumer
dispatch, clear behavior, or PCM writeback.

Evidence inputs: `scratch/agent/s3464_m5_retail_producer_value/oracle.log` and
`scratch/agent/s3460_m5_source_value_witness_retry/run.log`.
