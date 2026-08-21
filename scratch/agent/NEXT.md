# NEXT work unit (s2103)

HYPOTHESIS-ID: m5-audio-image-task-contract

## Work unit

Run one same-build control/treatment pair with the corrected host-only
stage-2/stage-3 to PCM join. The unit is admissible only if both arms
reach title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, and the
treatment emits at least one phase-gated hangar stage row with corrected
DMA-order `dma_nz_a=[1-9]`. Do not change task fields, DMA arguments, output
routing, canary, dispatch, waits, queue policy, or default audio behavior.
The current build already contains the corrected comparator; rebuild once
before launching both arms so the pair is visibly same-build.

## Competing hypotheses and discriminator

- **H-ImageDestIsPCM** — a corrected nonzero stage-2 or stage-3 row matches
  a PCM consumer by exact normalized destination, length, FNV, and nonzero
  count, and the task completion event precedes that consumer event. This
  identifies the image destination as the playback buffer at this scope.
- **H-ABI-Destination / H-ConsumerDifferentField** — corrected nonzero
  stage-to-DMA identity is present, but no PCM source/consumer row matches
  its exact address and payload. This keeps the boundary at task-field or
  consumer-buffer interpretation.
- **H-InputZero-at-Hangar** — no corrected nonzero stage row occurs after
  the hangar gate. This leaves the join unevaluable and moves no ABI
  conclusion; it would indicate the prior nonzero sample was not reproduced.
- **H-StageDmaMismatch** — a corrected nonzero stage row occurs but does not
  agree with the existing DMA range hash. This selects an instrumentation
  or address/length interpretation defect and forbids PCM inference.

The one-run table must report, by arm/ordinal/phase/stage, stage destination,
length, `dma_fnv_a`, `dma_nz_a`, existing DMA payload identity, PCM
callback identity, and event order. Report exact joins, stage-only rows,
consumer-only rows, and ordering violations separately. The route markers
and PCM source/consumer rows are positive controls; a counter firing alone
does not admit a null.

## Exact commands

From the repository root, build once:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Then launch these concurrently from separate shells:

```sh
env GAME_EXTRA_ENV='ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2103_image_join_control 30 12 > scratch/agent/s2103_image_join_control_driver.log 2>&1
env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1' PROBES_OVERRIDE='p1:start:0' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2103_image_join_treatment 30 12 > scratch/agent/s2103_image_join_treatment_driver.log 2>&1
```

The driver now bounds its screenshot helper with a five-second Python
subprocess timeout. If a driver still remains after its watchdog, identify
the exact process group and kill it with SIGKILL. Do not use SIGTERM. Inspect
logs with `grep`/`tail`, not by reading a whole run log.

## Expected outcomes

A corrected nonzero stage-to-DMA row plus an exact post-task PCM consumer
match selects H-ImageDestIsPCM. A corrected nonzero stage-to-DMA row with
no exact PCM match selects H-ABI-Destination/H-ConsumerDifferentField.
No corrected nonzero row is unevaluable, and a corrected stage/DMA mismatch
is an instrument/address defect rather than an audio conclusion.
