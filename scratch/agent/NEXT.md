# NEXT work unit (s2361) — M5 Step 1 stub/image validation

HYPOTHESIS-ID: m5-step1-stub-image-validation

## Work unit

Run one same-build port validation with `ROGUESQ_AUDIO_UCODE=0` and `=1`
arms. Retain the qualified route, eleven-Start input, task ABI/source,
image-stage/DMA, service/slot, PCM, voice/filter, and title/hangar phase
controls. Use the s2360 retail source relation as comparison only. Do not
write back a field, alter task data, change a consumer/default, or add a guard.

## Competing hypotheses and discriminating measurement

- H-Step1ImageClosesContract: the image arm changes DMEM, emits the expected
  DMA/stage rows, returns `Broke`, reaches SP completion, and produces the
  predicted service/slot/PCM downstream rows while matching the stub arm's
  title and hangar route. This selects the current image contract as the
  validated opt-in boundary.
- H-Step1ContractGap: the image arm has positive dispatch/DMEM/DMA/exit
  controls but lacks one or more task-field/source, service/slot, voice/reap,
  or PCM source/consumer joins. This keeps the image opt-in and identifies the
  first missing contract edge without changing it.
- H-Step1RouteOrArmInvalid: either arm lacks the positive route or task
  controls, crashes/aborts before the target phase, or loses the required
  phase-gated table. No audio conclusion is valid.
- H-Step1RouteOnly: both arms pass route/task controls, but the image arm's
  extra internal work does not produce the predicted downstream signal. This
  rejects a completion-only explanation and keeps the contract gap open.

The discriminator is one arm/phase table containing
`dispatch -> task fields/source -> DMEM/DMA -> image exit -> SP completion ->
service -> status/slot -> voice/reap -> MORT/filter -> PCM source -> PCM
consumer -> route phase`, plus stub/image deltas. Controls require positive
route/task rows for both arms, nonzero image DMEM/DMA rows for the image arm,
and the qualified title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`
phases. Select exactly one hypothesis from the table; do not infer success
from `Broke` alone.

## Exact commands

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2327_m5_task_ordinal_prepost_join.sh s2361_m5_step1_stub_image
    grep -E '^(controls|table|verdict) ' scratch/agent/s2361_m5_step1_stub_image/driver.log

The existing runner builds no separate arm: it runs both arms from the one
binary, kills each game with SIGKILL, and writes the phase-keyed tables under
`scratch/agent/s2361_m5_step1_stub_image/`. Reject the result if its oracle,
title/hangar, task ABI, VI, image-join, or PCM controls are absent.
