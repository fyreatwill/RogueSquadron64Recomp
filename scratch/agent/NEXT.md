# NEXT work unit — qualify the pre-title image route boundary

HYPOTHESIS-ID: m5-image-route-834c

The s3559 image/PCM join was route-invalid. Before building, the competing
hypotheses and one discriminator are:

- H-ImageInputBoundary: the image arm reaches `0x8000834C` with a malformed
  caller/input tuple; the complete table will show the first invalid pointer,
  caller, or producer before the crash/stall, with the retail counterpart
  valid in the same phase.
- H-ImageRouteGate: the image arm's task/audio dispatch or scheduler route is
  absent or diverges before `0x8000834C`, while caller inputs remain valid; the
  table will show route-control failure before the boundary and no equivalent
  image-side task progress.
- H-SharedContention: the failure requires another port instance; a single
  image arm will reach title 1024 and hangar 512, while the paired arm fails.

The single discriminator is one phase-keyed table covering image and silent
port arms plus independent retail controls: route phase, image-task dispatch,
`0x8000834C` entry/last guest PC, caller PC, all pointer/scalar arguments,
HMT/texture entry and return rows, task ordinal, service/SP completion, and
crash/stall outcome. Positive controls required in every valid arm are the
whole-RDRAM retail watch, port dispatch, title 1024, and hangar 512. A target
join is invalid unless the image arm reaches both target VIs.

Run the oracle control first, then build and run both arms together; also run
one image arm alone in the same iteration to test H-SharedContention. Use the
validated route and phase gate:

    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
      ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
      ROGUESQ_AUTOPILOT_STOP_WIDTH=512 \
      ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1 \
      ROGUESQ_LOG_AUDIO_RETURN=1 PROBE_PHASE_WIDTH=1024 \
      PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
      zsh tools/probe.sh scratch/agent/s3560_image_route 75 1

Use `ROGUESQ_AUDIO_UCODE=1` for image and `=0` for silent. Do not change task
fields, output, gates, slots, PCM, writeback, or add a guard. Outcomes select
the next step: H-ImageInputBoundary follows the first legitimate producer
with independent retail attribution; H-ImageRouteGate follows the missing
route edge; H-SharedContention is selected only if the alone arm reaches both
target VIs while the paired image arm fails. If all image arms remain
pre-target, record the route as unresolved and do not repeat the output join.
