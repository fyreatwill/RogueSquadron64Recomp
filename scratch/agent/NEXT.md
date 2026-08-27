# NEXT work unit (s2510) — separate concurrency from route/input divergence

HYPOTHESIS-ID: m5-image-concurrency-control

## Single work unit

Run one same-build concurrency control with the image arm fixed: compare a
single image process against an image process paired with a non-rendering
silent control, preserving the existing phase-relative input and positive
controls. Do not change audio implementation or add a mitigation. Capture
phase reached, image-task rows, first crash symbol/guest PC, and whether the
paired image misses the gate before any target null is interpreted.

## Competing hypotheses and discriminator

- `H-concurrent-resource`: adding the silent peer causes the image arm to
  miss the 1024 gate while the single image arm passes it.
- `H-route-input`: the paired image diverges for phase/input reasons that are
  independent of shared renderer pressure.
- `H-image-renderer-resource`: the single image arm reaches a reproducible
  renderer crash after its positive controls.

The discriminator is one same-build table of single-image versus
image-with-silent-pair: first/last VI phase, image-task count, crash symbol,
last guest PC, and crash/timeout. A target null is valid only if that arm's
image-task positive control fires; no writer claim is allowed unless the
target route is reached.

## Exact commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_PHASE=1 \
ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 \
ROGUESQ_LOG_M5_GATE_CONTRACT=1 zsh scratch/agent/run_s2510_image_concurrency.sh
```

The driver must launch the single image arm and the image-plus-silent pair
from `build/`, watchdog all processes, use identical phase-relative keys,
SIGKILL them, and write absolute logs under
`scratch/agent/s2510_m5_image_concurrency/`.
