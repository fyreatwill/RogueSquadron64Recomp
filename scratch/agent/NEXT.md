# NEXT work unit (s2105) — route-admission pair for corrected image join

HYPOTHESIS-ID: m5-audio-image-task-contract

## Work unit

Run one same-build control/treatment pair with the corrected host-only
stage-2/stage-3 to PCM join and `ROGUESQ_LOG_SPBOOT=1`. The admission
condition is both arms reaching title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400` in the same pair. Keep the existing route and PCM positive
controls; do not interpret a single-arm stage row as an audio conclusion.
Do not change task fields, DMA arguments, output routing, canary, dispatch,
waits, queue policy, or default audio behavior.

## Competing hypotheses and discriminator

- **H-PairedRouteRecovers** — both arms reach both target VIs. The full
  ABI/DMA table is admissible; a corrected nonzero stage-to-DMA row with an
  exact PCM consumer match selects `H-ImageDestIsPCM`, while a corrected
  nonzero row with no PCM match selects `H-ABI-Destination`/
  `H-ConsumerDifferentField`.
- **H-TreatmentPreHangarCrash** — control reaches hangar but treatment stops
  after title or before hangar. The crash symbol and last guest PC become the
  next M5 route boundary; treatment stage rows remain single-arm evidence.
- **H-ControlRouteFailure** — treatment reaches hangar but control stops
  before title or hangar. This selects a control/treatment route split and
  forbids PCM inference from that pair.
- **H-BothRouteFailure** — neither arm reaches both target VIs. The route
  recipe remains unevaluable and the next unit must isolate route admission
  before collecting another PCM table.

The discriminating measurement is the phase-gated pair table: per arm, record
title/hangar gates, process outcome, crash marker, last guest PC, ABI/DMA row
count, corrected nonzero stage count, exact PCM matches, stage-only rows, and
ordering violations. A counter firing without both route gates is not a
positive control for the join.

## Exact commands

From the repository root, rebuild once:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Launch both arms concurrently from separate shells:

```sh
env GAME_EXTRA_ENV='ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_SPBOOT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2105_image_join_control 30 12 > scratch/agent/s2105_image_join_control_driver.log 2>&1
env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_SPBOOT=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2105_image_join_treatment 30 12 > scratch/agent/s2105_image_join_treatment_driver.log 2>&1
```

Use SIGKILL for any remaining process group; inspect run logs with `grep` and
`tail`, never by reading them whole.
