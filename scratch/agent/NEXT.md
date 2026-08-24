# NEXT work unit (s2303) — M5 task-to-stage ordinal join

HYPOTHESIS-ID: m5-step3-task-stage-ordinal-join

## Work unit

Run one new M5 Step 3 contract capture using the already-qualified default
Factor 5 image arm and an independent retail oracle. Build one bounded table
joining every target-phase nonzero image-stage row by audio-task ordinal to its
DMA range and PCM source/consumer rows. Include both target origins when they
occur, task-field identity, destination/length/FNV/nonzero counts, source-before
consumer ordering, and the route phase. This is a new task→stage→PCM ordinal
join; do not repeat the s2291 writer join or the s2301 retail sequence table,
and do not change game behavior.

## Competing hypotheses and discriminating measurement

- H-TaskStageConsumerComplete: every nonzero phase-10/12 image-stage row has
  the same task ordinal and destination/length/hash/nonzero tuple in a DMA row
  and in both PCM endpoints, with source before consumer; the retail metadata
  writer remains a different contract edge.
- H-TaskStageOutputGap: at least one nonzero image-stage row has no same-ordinal
  DMA or PCM join, or has a destination/length/hash/order mismatch.
- H-RetailContractEquivalent: the independent retail task/output writer and
  the qualified port ordinal join agree on destination, length, payload class,
  and ordering at the measured target span.
- H-CoverageInvalid: the retail whole-RDRAM/title/hangar controls, the width-
  aware target bucket, or the port title/hangar route gate fails.

The discriminator is the complete arm/phase/task-ordinal table with columns
`phase,width,origin,task_ordinal,task_fields,stage,dest,len,stage_fnv,stage_nz,
dma_match,pcm_source_match,pcm_consumer_match,source_before_consumer`; every
non-coverage outcome selects one of the first three hypotheses. A row-count
counter alone is not sufficient.

## Exact commands

1. Ask ground truth before adding the join table:

   `grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|writer-pc-phase origin=0x006ab400 width=512 watch=2' scratch/agent/s2301_m5_target_sequence_join_extended/oracle.log | tail -80`

   The existing independent retail controls and target writer histogram must
   be present. If they are absent, repair the oracle recipe first; do not
   build the port join against an unqualified retail run.

2. Add the bounded ordinal join to a new driver/postprocessor. Run the retail
   oracle with the whole-RDRAM watch, title/hangar VI trace, width-aware target
   bucket, task/output span, and ring-span controls. Run one default image arm
   with `ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_LLE_FORCE=1`,
   `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, `ROGUESQ_SPIN_YIELD=1`,
   `PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, and the existing
   `audtask-abi`, `audtask-image-stage`, `audtask-dma-range`,
   `ROGUESQ_LOG_M5_HOST_BOUNDARY`, `ROGUESQ_LOG_PCM_BOUNDARY`, B40, and
   route-state diagnostics. Gate interpretation on title and hangar in the
   same run.

3. If the join is in runtime/generated code, build once:

   `cmake --build build --config Debug --target RogueSquadron64Recomp`

4. Syntax-check and run the new driver:

   `zsh -n scratch/agent/run_s2303_m5_task_stage_ordinal_join.sh`

   `zsh scratch/agent/run_s2303_m5_task_stage_ordinal_join.sh`

Report the complete table before interpreting any task/output field. No
writeback, consumer, writer, slot, gate, guard, address-remap, or default
change is authorized by this work unit.
