# NEXT work unit (s2133) — port stub/image PCM and AI boundary

HYPOTHESIS-ID: m5-pcm-ai-ordering

## Work unit

Execute M5 plan step 6's port-side same-build comparison now that the retail
oracle selected `H-RetailAIQueued`. Use the existing phase-gated audio-return,
PCM-boundary, PCM-sanity, and task-dispatch diagnostics. Build once, then run
the silent stub and opt-in `factor5_ucode_b` arms concurrently. Do not change
`osAiGetStatus_recomp`, task output routing, waits, guards, or the default
audio arm in this unit.

## Competing hypotheses and discriminator

- `H-PortAIQueueMatches`: both arms pass LLE/task positive controls and reach
  title/hangar; the image arm emits real audio-task return rows, host AI/PCM
  boundary rows, an exact source/consumer span join, and at least one
  nonzero `[pcm-sanity]` callback. The stub arm retains the silent contract.
  This selects the first port-side AI/PCM contract to preserve.
- `H-PortAIQueueSilent`: the image arm reaches the target and its task/PCM
  boundary controls fire, but every image `[pcm-sanity]` callback is all-zero
  or the host consumer has no nonzero join while the task returns. This keeps
  the host callback/decoder boundary open; it does not authorize an AI-status
  or routing change.
- `H-CoverageFailure`: either arm misses the target phase or its positive
  dispatch control, or the image arm produces no task/PCM rows. This selects
  no PCM hypothesis; do not interpret nulls.

The discriminator is one table keyed by arm and VI phase/origin: positive
LLE/audio dispatch counts; `audio-return` exit; `pcm-boundary-source` and
`pcm-boundary-consumer` address/count/full-span/nonzero joins;
`pcm-sanity` callback count and all-zero/nonzero counts; and target-phase
coverage. Select `H-PortAIQueueMatches` only when image nonzero PCM and an
exact source/consumer join co-occur after the controls. Select
`H-PortAIQueueSilent` only with target coverage, image task returns, and a
positive PCM callback control whose content remains zero. Any missing control
or target phase selects `H-CoverageFailure`.

## Exact commands

    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5step6_stub 30 12 > scratch/agent/m5step6_stub_driver.log 2>&1 &
    STUB_PID=$!
    env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5step6_image 30 12 > scratch/agent/m5step6_image_driver.log 2>&1 &
    IMAGE_PID=$!
    wait "$STUB_PID"; STUB_RC=$?
    wait "$IMAGE_PID"; IMAGE_RC=$?
    printf 'stub_rc=%s image_rc=%s\n' "$STUB_RC" "$IMAGE_RC"

Read `scratch/s73_post_a_scene/m5step6_stub/run.log` and
`scratch/s73_post_a_scene/m5step6_image/run.log` only with bounded grep/tail.
The work unit ends when the same-build table selects one hypothesis; do not
promote any host or task change from a silent/null result.
