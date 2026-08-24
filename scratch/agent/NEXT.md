# NEXT work unit (s2306) — M5 unconsumed-edge recurrence capture

HYPOTHESIS-ID: m5-step3-unconsumed-edge-attribution

## Work unit

Run one extended same-run M5 Step 3 capture using the qualified default Factor
5 image arm and an independent retail oracle. Retain the port for 45 seconds
after the first hangar origin, preserve the corrected `guest`→physical tuple
normalization, and report every nonzero stage tuple at both target origins.
The discriminator is whether the `0x166450`/`nz=621` stage-only tuple recurs
without an exact PCM tuple while the `0x166750`/`nz=639` tuple continues to
close at a delayed ordinal. Do not change game behavior or add writeback,
consumer, slot, gate, guard, or address-remap machinery.

## Competing hypotheses and discriminating measurement

- H-PersistentUnconsumedEdge: repeated `0x166450` nonzero stage tuples have
  exact DMA but no exact source or consumer tuple anywhere in the retained
  target phase, while the `0x166750` tuple has the expected delayed join.
- H-TransientStageOnly: a later nonzero `0x166450` tuple gets an exact source
  and consumer match with valid event ordering, so the first stage-only row was
  a phase/route capture artifact.
- H-PayloadTupleMismatch: PCM source/consumer calls for `0x166450` recur, but
  their length/FNV/nonzero tuple differs from the stage payload; the address
  path exists but the payload contract is not the same.
- H-CoverageInvalid: the retail whole-RDRAM/title/hangar controls, the
  target writer controls, width-aware target bucket, or port title/hangar
  route gate fails.

The discriminator is one complete recurrence table with columns
`phase,width,origin,task_ordinal,stage_event,dma_event,stage,dest,len,
stage_fnv,stage_nz,source_n,consumer_n,source_event,consumer_event,
source_delta,consumer_delta,dma_before_source,source_before_consumer`.
Add a per-destination summary counting exact tuple matches and mismatches.
Every non-coverage outcome selects one hypothesis; row counts without the
complete tuple table are insufficient.

## Exact commands

1. Ask ground truth before changing the driver or adding an instrument:

   `grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|writer-pc-phase origin=0x006ab400 width=512 watch=2|writer-pc pc=0x8008eb8c|writer-pc pc=0x8008ebbc|writer-pc pc=0x80094648' scratch/agent/s2305_m5_temporal_output_join/oracle.log | tail -80`

   Require the positive-control threshold, both VI origins, the target writer
   phase line, and all three writer-PC lines. If absent, repair the oracle
   recipe first; do not interpret a port recurrence capture against an
   unqualified retail run.

2. Create/update `scratch/agent/run_s2306_m5_temporal_recurrence.sh` from the
   s2305 driver. Change only the post-hangar retention to 45 seconds and add
   the per-destination exact-match/mismatch summary. Run the retail oracle
   with whole-RDRAM, title/hangar VI trace, width-aware target bucket,
   task/output span, and ring-span controls. Run one default image arm with
   `ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_LLE_FORCE=1`,
   `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`,
   `ROGUESQ_SPIN_YIELD=1`, and the existing `audtask-abi`,
   `audtask-image-stage`, `audtask-dma-range`,
   `ROGUESQ_LOG_M5_HOST_BOUNDARY`, `ROGUESQ_LOG_PCM_BOUNDARY`, B40, and
   route-state diagnostics. Gate interpretation on title and hangar in the
   same run. Run all measurement arms in this one iteration.

3. Syntax-check and run the driver:

   `zsh -n scratch/agent/run_s2306_m5_temporal_recurrence.sh`

   `zsh scratch/agent/run_s2306_m5_temporal_recurrence.sh`

Report the complete table before interpreting any task/output field. No
writeback, consumer, writer, slot, gate, guard, address-remap, or default
change is authorized by this work unit.
