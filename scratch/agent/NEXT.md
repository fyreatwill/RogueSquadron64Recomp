# NEXT work unit — identify the image-task output join

HYPOTHESIS-ID: m5-step3-image-output-join

Run one diagnostic-only, phase-gated comparison of the current image arm and
silent control. Do not change task fields, output, gates, slot values, PCM, or
writeback behavior. Use the validated route from s3558:

    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
      ROGUESQ_AUDIO_UCODE=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
      ROGUESQ_AUTOPILOT_STOP_WIDTH=512 ROGUESQ_LOG_M5_TASK_CONTRACT=1 \
      ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_AUDIO_RETURN=1 \
      PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
      PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
      zsh tools/probe.sh scratch/agent/s3559_m5_image_output 75 1

Build both image and `ROGUESQ_AUDIO_UCODE=0` arms together. The single
discriminator is a phase-keyed join table for each image-stage row:
`field348`, `field348+0x100`, stage `dest`, DMA source/range/hash, PCM source
and consumer address/range/hash/nonzero count, task ordinal, service return,
slot/status, voice/reap, and MORT class. Positive controls required for each
arm are route dispatch, title 1024, hangar 512, and SP completion.

- H-DestinationIsPCM: image `dest` or `field348+0x100` equals the nonzero PCM
  source/consumer span with matching ordinal and completion ordering.
- H-DestinationIsNotPCM: image stage and PCM are both live but their addresses,
  hashes, or ordering do not join; the next probe must follow the legitimate
  writer/consumer boundary.
- H-RouteOnly: either arm fails to reach both target VIs; all target nulls are
  unevaluable and the route recipe must be repaired before interpretation.

Do not implement Step 3 until the selected destination has an identified
writer and independent legitimacy evidence. If the complete table remains
unresolved, record the missing join and choose the highest-information-value
producer witness; do not add another counter field alone.
