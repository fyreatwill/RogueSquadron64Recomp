# NEXT work unit (s2511) — separate persistent sharing from startup-order divergence

HYPOTHESIS-ID: m5-image-concurrency-control

## Single work unit

Run one same-build staggered-start control: launch a single image process and
wait until its 1024 positive control fires, then launch the image-plus-silent
pair with the same phase-relative input. Keep the existing single-image arm
as the route control if capacity permits. Do not change audio implementation
or add a mitigation. Capture phase reached, image-task rows, first crash
symbol/guest PC, and whether the paired image misses the gate before any
target null is interpreted.

## Competing hypotheses and discriminator

- `H-concurrent-resource`: adding the silent peer causes the image arm to
  miss the 1024 gate while the single image arm passes it.
- `H-route-input`: the paired image diverges for phase/input reasons that are
  independent of shared renderer pressure.
- `H-image-renderer-resource`: the single image arm reaches a reproducible
  renderer crash after its positive controls.
- `H-startup-order`: the paired failure is caused by simultaneous process
  startup or early global initialization; staggering the pair after a live
  image target route prevents the pre-target failure.

The discriminator is one same-build table of the staggered paired-image arm
versus the single-image baseline: whether the pair reaches 1024 after the
image baseline is already live, image-task positive-control count, first crash
symbol, last guest PC, and crash/timeout. A target null is valid only if that
arm's image-task positive control fires; no writer claim is allowed unless the
target route is reached.

## Exact commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_PHASE=1 \
ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 \
ROGUESQ_LOG_M5_GATE_CONTRACT=1 zsh scratch/agent/run_s2511_staggered_image_concurrency.sh
```

The driver must launch the image baseline from `build/`, wait for its 1024
positive control, then launch the image-plus-silent pair, watchdog all
processes, use identical phase-relative keys, SIGKILL them, and write
absolute logs under
`scratch/agent/s2511_m5_staggered_image_concurrency/`.
