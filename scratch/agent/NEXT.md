# NEXT work unit (s2509) — isolate image-arm pre-title crash

HYPOTHESIS-ID: m5-image-pretitle-crash

## Single work unit

Reproduce the image arm's pre-title crash in a single image-arm run, then
compare it in the same build against a no-audio-control image configuration
that keeps the renderer and route identical. Use the qualified route and
phase logging, but do not change audio implementation or add a mitigation.
Capture the first native crash symbol, last guest PC, phase reached, and
whether the image task contract begins.

## Competing hypotheses and discriminator

- `H-image-renderer-resource`: the image arm alone reaches the same early
  renderer crash symbol/guest PC; removing image-task dispatch prevents it.
- `H-concurrent-resource`: the crash requires the concurrent image/silent
  pair or shared renderer pressure and disappears in a single image run.
- `H-route-input`: the image arm reaches a different phase or task boundary
  before failing, indicating an input/route divergence rather than renderer
  resource failure.

The discriminator is the same-build table of single-image versus
image-with-silent-pair: crash symbol, last guest PC, first/last VI phase,
dispatch count, task-contract count, and crash/timeout. A null is valid only
if the image task/phase positive control fires in that arm; no writer claim is
allowed unless the target route is reached.

## Exact commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_PHASE=1 \
ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 \
ROGUESQ_LOG_M5_GATE_CONTRACT=1 zsh scratch/agent/run_s2509_image_crash.sh
```

The driver must launch the single image arm and the image-plus-silent pair
from `build/`, watchdog both, use identical phase-relative keys, SIGKILL both,
and write absolute logs under `scratch/agent/s2509_m5_image_crash/`.
