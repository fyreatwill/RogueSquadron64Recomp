# Next work unit: M5 image-arm pre-target stability qualification

HYPOTHESIS-ID: m5-step1-contract-qualification

The native task-data value thread is parked after three consecutive paired
captures without a real-arm target fault. Do not add another page-watch field.

Competing hypotheses:

- `H-M5-ImageReachesTarget`: the image arm reaches title/hangar when paired
  with the silent control, allowing the complete contract row to qualify.
- `H-M5-ImagePreTargetCrash`: the real arm fails before target again, so the
  contract nulls remain unevaluable and the crash boundary is the next edge.
- `H-M5-ImageOnlyInterference`: the concurrent pair perturbs the real arm; an
  image-only arm reaches target while the silent control remains valid.

Discriminator: one build and one run retaining the same concurrent pair,
whole-RDRAM oracle, phase gates, and full Step 1 joins, with the image crash
boundary captured. A real target row selects `H-M5-ImageReachesTarget`; a
repeat pre-target crash with valid silent/oracle controls selects
`H-M5-ImagePreTargetCrash`; only an image-only target with a valid paired
control selects `H-M5-ImageOnlyInterference`.

Build once:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Run the existing validated real/silent phase-gated recipe from `build/` with
`ROGUESQ_AUDIO_UCODE=1/0`, LLE-solo, spin-yield, autopilot,
`PROBE_PHASE_WIDTH=1024`, and `PROBE_KEYS_FROM_PHASE=1`; if the pair dies
before target, run the image-only arm within the same work unit using the same
build and controls. Retain the existing M5 dispatch/task/DMA/service/slot/
voice/MORT/PCM logs and SIGKILL cleanup.
