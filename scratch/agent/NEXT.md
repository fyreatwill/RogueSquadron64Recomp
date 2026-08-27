# NEXT work unit (s2740) — validate SP yield de-stub

HYPOTHESIS-ID: m5-audio-yield-contract

## Work unit

Run one phase-gated, same-build validation of the new SP yield API state in the
qualified LLE route. Exercise the real image arm and silent control arm in the
same build, with the retail whole-RDRAM positive control and existing
audio/task/SP/PCM joins enabled. Do not claim task yielding unless a request,
yielded-status read, task exit, and SP completion join on the same task fields.

## Competing hypotheses and discriminator

- H-yield-observed: an audio task requests yield and the API reports it before
  a corresponding task/SP transition.
- H-yield-unused: the image and silent arms complete without any yield request
  or yielded-status observation in the target phases.
- H-yield-state-only: the API reports a request, but task exit/SP completion
  remain unchanged and no downstream audio edge moves.

The discriminator is one phase-keyed row joining yield request/status, task
identity and fields, task exit, SP completion, service/slot progress, PCM
source/consumer rows, and route phase (`1024 @ 0x00790400`, `512 @
0x006AB400`). The whole-RDRAM retail control must fire before narrow nulls are
interpreted.

## Exact commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_AUTOPILOT=1 ROGUESQ_LOG_ALL=1 ROGUESQ_AUDIO_UCODE=1 \
  ./build/Debug/RogueSquadron64Recomp
```
