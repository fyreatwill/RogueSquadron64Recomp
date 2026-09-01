# NEXT work unit — identify the image-task stage-output producer

HYPOTHESIS-ID: m5-image-task-output-producer

Session 3562 found a target-valid standalone image arm, but its stage output
was zero-valued and did not join PCM source/consumer rows. The concurrent pair
was route-invalid and is discarded for target-phase comparison. Continue at
the first legitimate producer of the stage destination. Before building, the
competing hypotheses and one discriminator are:

- H-StageWriterMissing: the stage destination is never legitimately populated;
  the producer census has no nonzero writer before task completion.
- H-StageWriterWrong: a legitimate writer populates a different destination or
  writes the wrong span; the census shows a stable divergent address/length.
- H-StageOutputValid: a legitimate writer populates the observed destination;
  the zero stage rows were a sampling or post-write interpretation error.

The single discriminator is one phase-keyed writer table for the image-stage
destination, including every candidate CPU store/DMA write, writer PC, value,
span, task ordinal, completion event, and the existing stage row. Positive
controls required in the valid image arm are title 1024, hangar 512, image
completion/DMA activity, and the existing PCM source/consumer controls. A
zero writer census is meaningful only after those controls fire.

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
guard. If a writer exists, follow its input producer; if no writer exists,
audit destination formation before completion. The retail oracle remains
optional until its core and ROM are present.
