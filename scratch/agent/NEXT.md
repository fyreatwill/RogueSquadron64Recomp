# NEXT work unit — split the pre-title image input and route boundaries

HYPOTHESIS-ID: m5-image-route-834c

Session 3560 refuted shared contention: paired and standalone image arms both
reached title 1024 and hangar 512 with task/return/PCM controls live. Before
building, the competing
hypotheses and one discriminator are:

- H-ImageInputBoundary: the image arm reaches `0x8000834C` with a malformed
  caller/input tuple; the complete table will show the first invalid pointer,
  caller, or producer before the crash/stall, with the retail counterpart
  valid in the same phase.
- H-ImageRouteGate: the image arm's task/audio dispatch or scheduler route is
  absent or diverges before `0x8000834C`, while caller inputs remain valid; the
  table will show route-control failure before the boundary and no equivalent
  image-side task progress.
- H-SharedContention: REFUTED by s3560; paired and standalone image arms both
  reached title 1024 and hangar 512.

The single discriminator is one phase-keyed table covering image and silent
port arms plus independent retail controls: route phase, image-task dispatch,
`0x8000834C` entry/last guest PC, caller PC, all pointer/scalar arguments,
HMT/texture entry and return rows, task ordinal, service/SP completion, and
crash/stall outcome. Positive controls required in every valid arm are the
whole-RDRAM retail watch, port dispatch, title 1024, and hangar 512. A target
join is invalid unless the image arm reaches both target VIs.

Run the oracle control first, then build and run both arms together with the
deeper caller/input/route instrumentation enabled. The image-alone arm is no
longer needed. Use the
validated route and phase gate:

    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
      ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
      ROGUESQ_AUTOPILOT_STOP_WIDTH=512 \
      ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1 \
      ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_CALLER_INPUT=1 \
      ROGUESQ_LOG_M5_HMT_INPUT=1 ROGUESQ_LOG_M5_BASE_INDEX=1 \
      ROGUESQ_LOG_M5_ROUTE_ORDER=1 ROGUESQ_LOG_M5_ROUTE_TRANSITION=1 \
      ROGUESQ_LOG_M5_ROUTE_HANDOFF=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 \
      ROGUESQ_LOG_M5_SELECTOR_ROUTE=1 ROGUESQ_LOG_VI_CALLERS=1 \
      PROBE_PHASE_WIDTH=1024 \
      PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
      zsh tools/probe.sh scratch/agent/s3560_image_route 75 1

Use `ROGUESQ_AUDIO_UCODE=1` for image and `=0` for silent. Add the existing
regeneration-safe caller/HMT/texture/route witnesses omitted from s3560, in
one build and one phase-keyed table. Do not change task fields, output, gates,
slots, PCM, writeback, or add a guard. Outcomes select the next step:
`H-ImageInputBoundary` follows the first legitimate producer with independent
retail attribution; `H-ImageRouteGate` follows the missing route edge. If both
arms remain target-valid without a divergence, close this route boundary and
resume the downstream image-task contract.
