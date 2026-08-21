# NEXT work unit (s2160) — A1 default-on flip

HYPOTHESIS-ID: m5-a1-default-on

## Work unit

s2159 selected `H-PolicyOnly`: every named host-contract reason to keep
`factor5_ucode_b` opt-in is closed by a selected hypothesis. Remaining
isolation is `get_rsp_microcode`'s env default plus historical comments.
Do not move the canary, change canary prefill, or change
`osAiGetStatus_recomp` / `osAiSetNextBuffer_recomp`.

This unit is the explicit A1 default-on flip of `s_use_real_audio_ucode`
in `src/main/main.cpp:get_rsp_microcode`:

    // after
    s_use_real_audio_ucode = (e && e[0] == '0') ? 0 : 1;

Unset / empty / any non-`0` value selects `&factor5_ucode_b_probe`.
`ROGUESQ_AUDIO_UCODE=0` remains the stub rollback. Refresh the stale
M_AUDTASK comment (dead M5-AUDIO-PLAN §3 crash-family pointer; "gate
still forced to 0"; "env var reproduces the hang") in the same edit.
Then one Debug build and a same-build unset vs `=0` title/hangar soak.

ORIGIN: the writer of the live `RspUcodeFunc*` is `get_rsp_microcode`
reading `ROGUESQ_AUDIO_UCODE`. Default-on selects `factor5_ucode_b`, the
legitimate retail audio image (s2135/s2136), not a wild value. The
previous default was a host stub.

## Competing hypotheses and discriminator

- `H-DefaultMatchesOptIn`: the unset arm matches the s2118 image-arm
  contract (title `1024 @ 0x00790400`, hangar `512 @ 0x006AB400`,
  `[audtask-dispatch] real_ucode=1`, `break_pc=0x1328`, `exit=Broke`,
  hangar stage-2 PCM joins). The `=0` arm matches the s2118 stub
  (`real_ucode=0`, `dma_count=0`, `break_pc=0`).
- `H-WaitWedgeOnDefault`: the unset (image) arm fails to reach title or
  hangar and the last live audio site is `waitForMusyXAudioTaskDone`.
- `H-RouteRegress`: the unset arm misses title or hangar without a
  wait-wedge signature (different last-guest-pc / crash family).
- `H-CoverageFailure`: either arm misses the target VI, so the pair
  cannot select among the first three.

Positive control: both arms must print `[audtask-dispatch]` with the
expected `real_ucode=` value before any target-phase comparison.

## Exact commands

After the default-on edit and one Debug build, from the repo root:

    env -u ROGUESQ_AUDIO_UCODE \
      ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 \
      zsh scratch/s73_post_a_scene/run_mission_keys.sh s2160_default_on 30 12

    env ROGUESQ_AUDIO_UCODE=0 \
      ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 \
      zsh scratch/s73_post_a_scene/run_mission_keys.sh s2160_default_off 30 12

Kill with SIGKILL. Compare `[audtask-dispatch] real_ucode=`, `[phase]`
title/hangar VIs, `break_pc`, and hangar PCM joins.

Do not change `osAiSetNextBuffer_recomp`, canary prefill, wait pumps, or
guest gates in this unit.
