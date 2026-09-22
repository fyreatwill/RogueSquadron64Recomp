# Next work unit: M5 retail writer-family join at the exact source boundary

HYPOTHESIS-ID: m5-retail-writer-family-join

Run one batched retail/port capture that retains the exact phase snapshots
from s3736 and joins the retail source-span writer PCs/order to the port
writer census around `0x800078EC`. Do not change port behavior or add a
mitigation. Keep whole-RDRAM, both target phases, and both real/silent port
controls mandatory.

Competing hypotheses:

- `H-RetailWriterEarlier`: retail nonzero bytes are produced by an earlier
  legitimate writer family before `0x800078EC`; the port lacks that writer or
  reaches it with different state.
- `H-RetailWriterSameButCleared`: retail and port share the producer, but the
  port's legitimate `0x800078EC` clear occurs before the image DMA while the
  retail target-phase ordering differs.
- `H-RetailLayoutContract`: the exact retail positions belong to a different
  source object despite the matching descriptor, so the apparent writer join
  is a layout/ownership mismatch.

Discriminator: in one run, the retail target-phase writer-PC histogram and
ordered source-span rows must identify whether nonzero stores occur before or
after `0x800078EC`; the port real arm must provide the corresponding ordered
writer rows and zero-payload DMA rows, while the silent arm and whole-RDRAM
control pass. An earlier retail writer with no port counterpart selects
`H-RetailWriterEarlier`; same writer plus different clear ordering selects
`H-RetailWriterSameButCleared`; only a descriptor/position mismatch with a
matching writer selects `H-RetailLayoutContract`. Missing any control or
phase is unevaluable.

Exact command basis: adapt
`scratch/agent/run_s3733_m5_retail_source_payload.sh` and
`scratch/agent/run_s3730_m5_source_layout.sh`; add the s3736
`--phase-snapshot-watch 1 --phase-snapshot-watch 2` oracle options and keep
`ROGUESQ_LOG_M5_SOURCE_TRANSITION=1`, `ROGUESQ_LOG_M5_SOURCE_WRITER=1`, and
`ROGUESQ_LOG_M5_INPUT_WRITER=1` in both port arms.
