# NEXT work unit (s2305) — M5 delayed-vs-unconsumed temporal output join

HYPOTHESIS-ID: m5-step3-task-stage-ordinal-join

## Work unit

Run one new M5 Step 3 contract capture using the qualified default Factor 5
image arm and an independent retail oracle. Keep the complete nonzero
stage→DMA→PCM table, but match the exact destination/length/FNV/nonzero tuple
across a bounded ±64 task-ordinal window, not only at the stage row's ordinal.
Record the nearest source and consumer ordinals/events, ordinal deltas, task
and DMA event order, and both target origins when present. Do not change game
behavior.

## Competing hypotheses and discriminating measurement

- H-DelayedPCMPublication: each nonzero stage tuple has an exact PCM source
  and consumer match at another ordinal within ±64, with DMA before source and
  source before consumer; the s2304 same-ordinal gap is queue timing.
- H-StageUnconsumed: at least one nonzero stage tuple has no exact PCM source
  or consumer match anywhere in the ±64 target-phase ordinal window, despite
  an exact DMA match at the stage ordinal.
- H-OrdinalWindowTooNarrow: a same-payload PCM match exists outside ±64, so
  the bounded window was insufficient and no consumer conclusion is valid.
- H-CoverageInvalid: the retail whole-RDRAM/title/hangar controls, the
  target writer controls, width-aware target bucket, or port title/hangar
  route gate fails.

The discriminator is one complete table with columns
`phase,width,origin,task_ordinal,stage_event,dma_event,stage,dest,len,
stage_fnv,stage_nz,source_n,consumer_n,source_event,consumer_event,
source_delta,consumer_delta,dma_before_source,source_before_consumer`.
Every non-coverage outcome selects one hypothesis; row counts alone are
insufficient.

## Exact commands

1. Ask ground truth before building the temporal join:

   `grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|writer-pc-phase origin=0x006ab400 width=512 watch=2|writer-pc pc=0x8008eb8c|writer-pc pc=0x8008ebbc|writer-pc pc=0x80094648' scratch/agent/s2304_m5_task_stage_ordinal_join/oracle.log | tail -80`

   Require the positive-control threshold, both VI origins, the target writer
   phase line, and all three writer-PC lines. If absent, repair the oracle
   recipe first; do not build the port temporal join against an unqualified
   retail run.

2. Create/update the bounded temporal-join driver/postprocessor. Run the
   retail oracle with whole-RDRAM, title/hangar VI trace, width-aware target
   bucket, task/output span, and ring-span controls. Run one default image arm with
   `ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_LLE_FORCE=1`,
   `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`,
   `ROGUESQ_SPIN_YIELD=1`, and the existing `audtask-abi`,
   `audtask-image-stage`, `audtask-dma-range`,
   `ROGUESQ_LOG_M5_HOST_BOUNDARY`, `ROGUESQ_LOG_PCM_BOUNDARY`, B40, and
   route-state diagnostics. Gate interpretation on title and hangar in the
   same run. Build all measurement arms in this one iteration.

3. If the temporal join is in runtime/generated code, build once:

   `cmake --build build --config Debug --target RogueSquadron64Recomp`

4. Syntax-check and run the driver:

   `zsh -n scratch/agent/run_s2305_m5_temporal_output_join.sh`

   `zsh scratch/agent/run_s2305_m5_temporal_output_join.sh`

Report the complete table before interpreting any task/output field. No
writeback, consumer, writer, slot, gate, guard, address-remap, or default
change is authorized by this work unit.
