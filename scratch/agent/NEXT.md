# NEXT work unit (s2588) — execute the first documented M5 de-stub step

HYPOTHESIS-ID: m5-audio-destub-sequence

## Single work unit

Read `docs/M5-AUDIO-PLAN.md`, select its first still-pending incremental
de-stub step, and implement only that step through the regeneration-safe build
path. Keep the silent `ROGUESQ_AUDIO_UCODE=0` arm available as the rollback
control. Do not change a gate, store, task field, output pointer, or add a
mitigation to bypass the known scene-graph boundary.

## Competing hypotheses and discriminator

- `H-AudioDegeneracy`: the selected de-stub changes the audio-disabled
  degenerate path and removes or moves the target failure.
- `H-UnrelatedBoundary`: the selected de-stub leaves the same
  `get_function`/scene-graph boundary and target phases remain absent.
- `H-NewAudioFailure`: the de-stub reaches a new audio-specific trap or crash.

The discriminator is a same-build silent-vs-image comparison, phase-gated by
VI transitions, with positive controls for audio dispatch, image entry/return,
and the selected step's intended output. Title/hangar reachability or a new
audio-specific failure splits the hypotheses; an unchanged 640 abort selects
only the unrelated-boundary hypothesis. Batch every counter needed for this
table in one build and one run.

## Required preparation

Follow the exact regeneration order in `AGENTS.md` and the plan. Run the
resulting image and silent arms from `build/`, kill each game with SIGKILL,
and capture logs under `scratch/agent/` with non-dot final path components.
Before building, document the selected step's competing hypotheses and
discriminator here with its exact positive control.
