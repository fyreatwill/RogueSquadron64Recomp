# Next work unit: audit the first nonzero retail source-span writers

HYPOTHESIS-ID: m5-step4-source-writer-counterpart

Session 4170 selected H-producer-context-mismatch. The independent retail
oracle saw 664 nonzero post-store bytes in the target span
`0x00178C80:0x00178F18`, while the port reached both target phases but its
source-span rows stayed `FNV=0x762B22A5`, `nz=0`. The shared `0x800078EC`
clear is a control; do not change it or add a mitigation.

Run one concurrent retail/port comparison using
`scratch/agent/run_s4148_m5_source_callsite.sh` as the harness. Keep the
whole-RDRAM positive control, `PROBE_PHASE_WIDTH=1024`,
`PROBE_KEYS_FROM_PHASE=1`, and the real-audio/LLE/ungated/solo route. Add
retail `--pc-hist-watch 1 --post-value-watch 1 --watch-pc 0x800078EC` and
keep `ROGUESQ_LOG_M5_SOURCE_CONTEXT=1`,
`ROGUESQ_LOG_M5_SOURCE_PRODUCER=1`, `ROGUESQ_LOG_M5_SOURCE_WRITER=1`,
`ROGUESQ_LOG_M5_TASK_CONTRACT=1`, and `ROGUESQ_LOG_PCM_BOUNDARY=1`.

Competing hypotheses and discriminator:

- H-writer-counterpart-parity: the first nonzero retail writers
  (`0x80090268`, `0x80090278`, `0x8008FF*` first) have matching port PCs,
  destinations, and nonzero values; the zero payload is later.
- H-writer-counterpart-mismatch: a retail nonzero writer has no matching port
  row, or the port row has a different context/destination/value; select that
  writer as the next source audit boundary.
- H-route-invalid: either arm misses the positive control or title/hangar VI,
  so writer and PCM nulls are unevaluable.

The result table must include route/positive-control status, retail writer-PC
and value rows, port counterpart PC/context/destination/value rows, source-span
FNV/nz, image task input, and PCM source/consumer. If parity holds, move to the
next producer layer; if mismatch holds, investigate the first missing or
zero-valued counterpart. Do not change behavior.
