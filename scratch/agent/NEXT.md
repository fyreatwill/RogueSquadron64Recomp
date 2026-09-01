# NEXT work unit — close the downstream image-task output contract

HYPOTHESIS-ID: m5-image-task-contract-gap

Session 3561 found the image arm target-valid standalone, but the requested
caller/HMT/base-index/task/selector table was absent. The route boundary is
closed at this evidence level; continue the qualified downstream image-task
contract. Before building, the competing hypotheses and one discriminator
are:

- H-ImageTaskOutputGap: image task DMA/completion reaches the target phase but
  its output span does not join the PCM source/consumer or named slot/MORT
  state; the complete table shows a missing destination-to-consumer join.
- H-ImageTaskConsumerRoute: the image output is formed, but the downstream
  consumer/slot route is absent or diverges; the table shows valid output with
  no matching consumer or slot transition.
- H-ImageContractParity: image output, PCM, slot/status, and MORT witnesses
  join with stable addresses and ordinals; this closes the current boundary.

The single discriminator is one phase-keyed table covering image and silent
port arms plus the independent retail control when the oracle is available:
image-task ABI/DMA/output rows, PCM source/consumer address and content,
audio ordinal, named slot/status transitions, MORT entry/return, and
task/service completion. Positive controls required in every valid arm are
port dispatch, title 1024, hangar 512, image PCM nonzero, and silent PCM zero.
Do not treat absent slot/MORT rows as a null unless the image arm reaches both
target VIs and the controls fire.

Run the oracle control first if its core and ROM are present. Then build once
and run image and silent arms together with the existing task-contract,
PCM-boundary, audio-return, task-handoff, slot/status, voice, and MORT
witnesses. Use the validated route and phase gate from s3561:

    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
      ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
      ROGUESQ_AUTOPILOT_STOP_WIDTH=512 \
      ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1 \
      ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_DOWNSTREAM=1 \
      ROGUESQ_LOG_M5_TASK_LIFETIME=1 ROGUESQ_LOG_M5_COMPLETION_CALL=1 \
      ROGUESQ_LOG_M5_VOICE_SLOTS=1 ROGUESQ_LOG_FILTER_VOICE_AUDIT=1 \
      PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
      PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
      zsh tools/probe.sh scratch/agent/s3562_image_contract 75 1

Use `ROGUESQ_AUDIO_UCODE=1` for image and `=0` for silent. Do not change
task fields, output, gates, slots, PCM, writeback, or add a guard. If image
output does not join, follow the first legitimate producer; if output joins
but the consumer is absent, follow that route edge; if all joins are present,
close this boundary.
