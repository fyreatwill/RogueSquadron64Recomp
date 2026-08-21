# NEXT work unit (s2102)

HYPOTHESIS-ID: m5-audio-image-task-contract

## Work unit

Add one host-only, regeneration-stable join between the existing image-stage
rows and the PCM callback. Extend the existing `rs64_audio_image_stage` path
in `src/main/main.cpp` to retain stage-2 (`0x6F0`) and stage-3 (`0xCB0`)
records keyed by audio ordinal, row, VI phase, destination, length, FNV, and
nonzero count. At the existing PCM callback boundary, join every source and
consumer row against those records and report exact destination/payload
identity plus event order relative to task completion. This is observation
only: do not change task fields, DMA arguments, output routing, canary,
dispatch, waits, queue policy, or default audio behavior.

The independent retail ground-truth gate is already satisfied by s2101:
whole-RDRAM control and both target VIs fired, and neither sampled exact
destination range had a phase-gated retail write. Do not add another broad
retail watch before this port join.

## Competing hypotheses and discriminator

- **H-ImageDestIsPCM** — a nonzero stage-2 or stage-3 row matches a PCM
  consumer by exact RDRAM destination, byte length, FNV, and nonzero count;
  the task completion event precedes the consumer event. This identifies the
  image destination as the playback buffer at the sampled scope.
- **H-Stage3IsPCM** — stage 2 does not match, but stage 3 does. This identifies
  the final `0xCB0` writeback as the consumer-facing buffer and stage 2 as an
  intermediate or metadata path.
- **H-ABI-Destination** — stage rows are nonzero and task/DMA rows remain
  live, but the PCM source/consumer uses a different address or payload and
  no exact stage match exists. This selects a task-field/destination
  interpretation boundary without changing the field.
- **H-ConsumerBoundary** — an exact stage row exists but no post-task PCM
  consumer is observed, or the consumer is zero/ordered before the task.
  This keeps the remaining boundary at callback/queue handoff rather than
  explaining it as an input or transform loss.

The discriminating table is one same-build A/B collection with rows keyed by
arm, ordinal, phase, stage, destination, length, stage FNV/nonzero, callback
kind, callback RDRAM, callback length, callback FNV/nonzero, and event order.
The unset-env control must reach title and hangar and fire the existing route
and PCM positive controls. The treatment must reach both target VIs and emit
stage rows; otherwise the treatment arm is unevaluable and no ABI conclusion
is allowed. Report exact matches, stage-only rows, consumer-only rows, and
ordering violations separately.

## Build and run

Implement the table in `src/main/main.cpp` and the smallest needed declaration
or event helper in the existing audio-join code. If generated output needs a
new callsite, update `tools/fixup_factor5_ucode.py` and run the required
regeneration order before CMake; do not hand-edit generated output. Build both
arms together:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run the qualified control and opt-in treatment concurrently from separate
shells, using the existing title-to-hangar driver and the reduced screenshot
probe. Use `PROBES_OVERRIDE='p1:start:0'`, keep
`ROGUESQ_SPIN_YIELD=1`, and arm `ROGUESQ_LOG_ALL=1`,
`ROGUESQ_LOG_PCM_SANITY=1`, `ROGUESQ_LOG_PCM_BOUNDARY=1`,
`ROGUESQ_LOG_WAITFORSLOT_GUARD=1`, `ROGUESQ_LOG_AUDIO_DRAIN=1`, and
`ROGUESQ_LOG_AUDIOTICK_TRACE=1` in both arms. The control leaves
`ROGUESQ_AUDIO_UCODE` unset; the treatment sets it to `1`:

```sh
env GAME_EXTRA_ENV='ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2102_image_join_control 30 12
env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2102_image_join_treatment 30 12
```

Capture each run's log under `scratch/agent/` and kill the whole process
group with SIGKILL if a driver remains after its watchdog. A null is valid
only with the same-run route positive controls and target VI markers.
