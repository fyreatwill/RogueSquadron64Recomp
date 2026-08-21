# NEXT work unit (s2094)

HYPOTHESIS-ID: m5-audio-pretarget-return-boundary

## Work unit

First retain the s2092 retail oracle positive control (whole-RDRAM watch,
title `1024 @ 0x00790400`, hangar `512 @ 0x006AB400`). Then add one
host-side, regeneration-independent wrapper in `src/main/main.cpp` around the
selected audio function for both arms. The wrapper must log a bounded,
per-dispatch row containing arm, phase/VI, ordinal, and the returned
`RspExitReason`, then return the same reason unchanged. Build once and run the
default silent-stub control and the opt-in image treatment concurrently from
the same eleven-Start driver. Do not change the guest gate, waits, guards,
host output routing, default dispatch, or target-phase filters.

## Competing hypotheses and discriminator

- **H-PostTaskRouteBoundary** — treatment dispatches and returns `Broke` for
  each observed pre-title task, as the control stub does, before the RT64
  crash. The image function has crossed its return boundary; the next issue is
  downstream route/state interaction, not a non-returning task.
- **H-ImageTaskExitBoundary** — treatment dispatches but produces no matching
  return, or returns a non-`Broke` reason, before the crash. The image task's
  execution or exit contract remains the immediate boundary.
- **H-ControlProbeFailure** — the control does not show one wrapper return per
  audio dispatch with `Broke`; the new instrument is invalid and the run is
  unevaluable.
- **H-RouteRecovered** — treatment returns and reaches both target phases in
  this run. The prior treatment-only route failure is not reproduced and the
  task/PCM discriminator can be resumed from phase-keyed rows.

The discriminator is the same-run dispatch-to-return table, with the control
one-to-one `musyx_stub` return as the positive control. A complete treatment
return table with `Broke` plus a pre-title RT64 crash selects
H-PostTaskRouteBoundary. A missing/non-`Broke` treatment return selects
H-ImageTaskExitBoundary. A treatment that reaches both target VIs selects
H-RouteRecovered and permits the existing ABI/canary/slot/PCM table to be
interpreted. A missing control join is unevaluable; do not infer from a
counter-only dispatch hit.

## Exact commands

Before editing/building the wrapper, rerun the fixed s2092 retail oracle
command from the Session 2092 entry and require its whole-RDRAM positive
control plus both target VIs. Then build once:

```sh
tools/oracle/build.sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 70 --hit-cap 64 --watch-write 0x0:0x800000 --watch-write 0xA0F50:0xA0F54 --watch-write 0x14998A:0x14998C --watch-write 0x14974C:0x149750 --first-watch 0 --detail-watch 1 --pc-hist-watch 1 --post-value-watch 1 --post-value-watch 2 --post-value-watch 3 --post-value-pc 0x8008EA34,0x8008EB40,0x8008EB7C,0x8008EC88,0x8008ED48 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run both arms concurrently:

```sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_AUDIO_RETURN=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step3-treatment 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/m5-audio-step3-treatment-driver.log 2>&1 &
pid_t=$!
env -u ROGUESQ_AUDIO_UCODE ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_AUDIO_RETURN=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step3-control 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/m5-audio-step3-control-driver.log 2>&1 &
pid_c=$!
wait $pid_t; rc_t=$?
wait $pid_c; rc_c=$?
printf 'treatment_rc=%s control_rc=%s\n' "$rc_t" "$rc_c"
```

Inspect bounded phase/return summaries from both run logs. If the treatment
again misses both target VIs, classify only the return boundary; do not use the
pre-target PCM rows to decide the task ABI or audio output contract.
