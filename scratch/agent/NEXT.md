# NEXT work unit (s2115) — same-run M5 image-task contract validation

HYPOTHESIS-ID: m5-audio-image-task-contract

## Work unit

Run one fresh, same-build paired validation of the default silent audio stub
and `ROGUESQ_AUDIO_UCODE=1` image arm concurrently. The s2114 pair and its
explicit-LLE retry were both pre-target coverage failures, so do not compare
their empty target tables. The new pair must reach at least one target phase
(`1024 @ 0x00790400` or `512 @ 0x006AB400`) before any contract comparison is
used. Reuse the s2113 phase-keyed contract witness and the existing route,
ABI/DMA, stage, slot, PCM, wait, queue, and VI controls. Do not change task
fields, DMA, exit mapping, output routing, canary handling, slots, PCM, waits,
guards, queues, or default behavior.

## Competing hypotheses and single discriminator

- H-TaskExitMapping: the generated completion edge at guest PC `0x1328` is
  legitimate, and host `Broke` with `output_buff=0` is compatible with the
  matched output/PCM data.
- H-OutputRoute: the image task produces valid data, but the host output field
  or route names a different buffer than the consumer uses.
- H-WritebackLoss: generated DMA is valid, but host writeback or task-field
  handling loses it before the canary/consumer boundary.
- H-NoValidOutput: the final task data is invalid or zero despite positive
  dispatch, so no host contract change is justified.

The discriminator is one phase-keyed stub/image table joined on target phase,
task ordinal, stage, guest span, full-span hash/nonzero count, break PC, exit,
output buffer, canary, slot status, and PCM source/consumer span. A same-phase
valid-span match through DMA and PCM with `Broke` selects H-TaskExitMapping;
different output/consumer destinations select H-OutputRoute; valid generated
DMA followed by failed host writeback selects H-WritebackLoss; zero/invalid
final data selects H-NoValidOutput. If either arm has positive dispatch/DMA
but no joined target row, classify that as coverage/recipe failure and do not
infer a contract result.

## Exact commands

Use the already-built Debug binary. Launch both arms concurrently from the
repository root:

    env GAME_EXTRA_ENV='ROGUESQ_M5_B40_VALUE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_WAIT_CONTRACT=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2115_m5_task_stub_pair 30 12 > scratch/agent/s2115_m5_task_stub_pair_driver.log 2>&1
    env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_B40_VALUE=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_WAIT_CONTRACT=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2115_m5_task_image_pair 30 12 > scratch/agent/s2115_m5_task_image_pair_driver.log 2>&1

If a launched process remains after its driver exits, terminate its process
group with SIGKILL. Inspect only phase-keyed counts, positive-control rows,
joined contract rows, and log tails; never read a complete run log. The retail
oracle control from s2113 already passed, so do not add instrumentation or
rebuild unless the source/build is changed.
