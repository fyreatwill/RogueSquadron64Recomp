# NEXT work unit — identify the image-task DMEM producer

HYPOTHESIS-ID: m5-image-task-output-producer

Session 3563 found the legitimate image-stage DMA writer, but its source DMEM,
DMA payload, and destination were all zero. The concurrent pair remains
route-invalid and is discarded. Continue at the first producer feeding the
stage DMEM windows. Before building, the competing hypotheses and one
discriminator are:

- H-DmemProducerMissing: no legitimate producer populates the stage DMEM
  windows before the image-stage hooks; the producer census remains zero.
- H-DmemProducerWrong: a legitimate producer writes a divergent DMEM span or
  transforms the wrong source; the census shows a stable address/length or
  transform mismatch.
- H-DmemPayloadValid: a legitimate producer populates the observed DMEM
  windows and the zero hash was a later clearing/interpretation error.

The single discriminator is one phase-keyed producer table for DMEM
`0x6F0..0x9F0` and `0xCB0..0xE48`, including every scalar/vector store or DMA,
writer PC, value/hash, span, task ordinal, and the existing stage/DMA row.
Positive controls required in the valid image arm are title 1024, hangar 512,
image completion/DMA activity, and the existing PCM source/consumer controls.
A zero producer census is meaningful only after those controls fire.

Run the oracle control first if its debugger core and retail ROM are present.
Then build once and run the target-valid standalone image recipe:

    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
      ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
      ROGUESQ_AUTOPILOT_STOP_WIDTH=512 \
      ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 \
      ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_AUDIO_RETURN=1 \
      ROGUESQ_LOG_M5_DOWNSTREAM=1 ROGUESQ_LOG_M5_TASK_LIFETIME=1 \
      ROGUESQ_LOG_M5_COMPLETION_CALL=1 ROGUESQ_LOG_M5_VOICE_SLOTS=1 \
      ROGUESQ_LOG_FILTER_VOICE_AUDIT=1 PROBE_PHASE_WIDTH=1024 \
      PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
      zsh tools/probe.sh scratch/agent/NEXT_IMAGE_STAGE_WRITER 75 1

Do not change task fields, output, gates, slots, PCM, writeback, or add a
guard. If a producer exists, follow its input; if no producer exists, audit
the DMEM staging/clear formation before completion. The retail oracle remains
optional until its core and ROM are present.
