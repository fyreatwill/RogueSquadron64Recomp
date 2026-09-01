# NEXT work unit — requalify the canonical heap-route capture

HYPOTHESIS-ID: m5-heap-route-requalification

Run one canonical real-audio/LLE-solo/spin-yield/autopilot capture from
build/ with the already-built caller-table binary, using the C88 route aid
and the phase gate. Do not add instrumentation or change heap/audio state.
Use ROGUESQ_AUTOPILOT=1, ROGUESQ_M5_C88_VALUE=0, ROGUESQ_AUDIO_UCODE=1,
ROGUESQ_SPIN_YIELD=1, ROGUESQ_LLE_FORCE=1, ROGUESQ_LLE_UNGATED=1,
ROGUESQ_LLE_SOLO=1, ROGUESQ_STUB_MISSING_FUNCS=1,
ROGUESQ_LOG_HEAP_DEQUEUE=1, PROBE_PHASE_WIDTH=1024,
PROBE_PHASE_TIMEOUT=180, PROBE_KEYS_FROM_PHASE=1, and PROBE_LEAVE_OK=1.

Competing hypotheses and the discriminator:

- H-RouteRequalifies: target phases return, making the caller/entry join
  evaluable.
- H-RouteStill640: positive controls fire but VI 1024 never arrives; the
  current caller hypotheses remain unevaluable and the next unit must inspect
  the 640 route blocker.
- H-RouteCrashes: a crash occurs before the gate; classify only with a crash
  marker and last guest PC.
- H-ControlsInvalid: autopilot or the phase control is absent; discard the run
  and fix the recipe.

The discriminating measurement is the same-run control/phase table:
autopilot arm and fire, VI 1024 and 512, heap-entry rows, and caller rows.
Only if both target VIs and heap-entry rows are live may caller rows be joined
by phase and ordinal; edge 1 versus edge 2 then selects the caller path,
while neither edge selects an alternate path. Missing controls make the
capture invalid.

Capture under scratch/agent/s3554_m5_heap_route_requalify/ with SIGKILL
cleanup. Do not change heap, audio, PCM, image-task, output, or texture-record
writes.
