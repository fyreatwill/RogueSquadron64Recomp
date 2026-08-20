# NEXT work unit (s2001) — validate the opt-in audio RSP arm

HYPOTHESIS-ID: m5-audio-ground-truth

## Single work unit

Use the regenerated tree from s2000 and one build to compare the default
`musyx_stub` control with `ROGUESQ_AUDIO_UCODE=1`. Add one batched host probe
around `lib/N64ModernRuntime/librecomp/src/rsp.cpp:run_task`; it must record
task type, selected arm, pre/post DMEM canary, and `RspExitReason` in the same
row. Do not reverse another `0xF50` store, remove a guard, enable
stock `aspMain`, or change the default dispatch.

## Competing hypotheses and discriminating measurement

- **H-degenerate-host-path:** the opt-in `factor5_ucode_b` arm completes audio
  tasks with `Broke`, preserves the DMEM canary, produces a live slot-byte
  transition, and reaches nonzero PCM; the default arm remains a clean stub
  control. This selects the current RSP/host path for the next M5 step.
- **H-MORT-path:** the opt-in arm dispatches but cannot produce valid voice
  descriptors or PCM, while DMEM remains intact; an independent retail/task
  attribution then selects the MORT boundary before further de-stubbing.
- **H-MusyX-mismatch:** the opt-in arm returns an unexpected exit, hangs, or
  corrupts its DMEM canary, with no valid slot/PCM transition. Keep it opt-in
  and treat the task-format mismatch as the next boundary.
- **H-scheduler-independent:** control and treatment have the same audio-arm
  completion and slot/PCM result but reproduce the status-3 worker freeze;
  that selects the parked scheduler-dispatch investigation separately.

The discriminator is one phase-gated table for both arms: visible
`[audtask-dispatch]` positive control, direct audio `RspExitReason`, pre/post
DMEM canary equality, guest slot status `0x02`→`0x00` or its named failure,
and `[pcm-sanity] all_zero=0` versus all-zero. A missing row without the
same-run graphics/task control is UNEVALUABLE.

## Exact commands

```sh
cmake --build build --target RogueSquadron64Recomp

env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_SPBOOT=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step2-control 30 12
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_SPBOOT=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step2-treatment 30 12
```

Run both arms from this same build and phase schedule, with separate capture
directories; use SIGKILL if the driver does not terminate the game itself.
The scheduler yield is common frontend reachability control, not an audio
fix. Record the phase-1024/title and hangar `VI 512 / 0x006AB400` rows before
interpreting any null. Roll back by unsetting `ROGUESQ_AUDIO_UCODE`.
