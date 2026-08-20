# NEXT work unit (s2067)

HYPOTHESIS-ID: m5-audio-image-output-contract

## Work unit

Run one phase-gated live task/value crosswalk on the qualified C88=1,
spin-yield route. Use the existing `[audtask-abi]`, `[audtask-dma-row]`, and
`[audtask-dma-range]` probes; do not add instrumentation, regenerate, build,
or change task fields, dispatch, guards, or guest behavior. The immediate
post-probe SIGKILL is only a capture boundary, so a late malformed DMA cannot
invalidate rows already collected. Reject the run if it dies before both
target phases or emits a crash/abort marker before the harness kill.

## Competing hypotheses and discriminator

- **H-ImageOutputField** — an exact target-phase `0xE50/0x180` or
  `0xCB0/0x198` effective RDRAM span overlaps the live OSTask
  `output_buff` or `yield_ptr` interval, and the corrected retail writer watch
  attributes that same span to the retail audio path.
- **H-ImageDataStruct** — neither output/yield interval overlaps, but the
  effective span overlaps the task-data interval reached from `data_ptr`, with
  matching retail writer ownership.
- **H-ImageTaskAbiMismatch** — complete target-phase rows show no field
  overlap or an offset/length mismatch for the exact generated spans; the
  canary is then an ABI/staging defect.
- **H-OutputRouteUnevaluable** — either target phase, the exact span, the
  no-crash control, or the independent retail writer/positive-control line is
  missing.

The discriminator is one joined table keyed by task row and phase:
`dmem,len`, effective RDRAM span, `output_buff`/`yield_ptr`/`data_ptr`
intervals, all overlap flags, `exit/canary`, and the retail writer-PC hits for
the same physical span. Output/yield overlap plus matching retail ownership
selects H-ImageOutputField; data-only overlap plus matching ownership selects
H-ImageDataStruct; complete no-overlap/offset mismatch selects
H-ImageTaskAbiMismatch; any missing control selects H-OutputRouteUnevaluable.

## Exact commands

Ground truth comes first. Rice video is required; the prior no-video command
was measured to remain at VI 320 and is invalid for this discriminator.

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 60 --vi-trace --pif-trace \
  --watch-write 0x0:0x800000 \
  --watch-write 0x166000:0x17A000 \
  --first-watch 1 --pc-hist-watch 1 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2067_oracle.log 2>&1

env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1' \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s2067_task_abi 0 12

PORT=scratch/s73_post_a_scene/s2067_task_abi/run.log
rg '^\[(phase|audtask-abi|audtask-dma-row|audtask-dma-range)\]' "$PORT" \
  > scratch/agent/s2067_task_abi_rows.log
rg -n 'dmem=0xE50 len=0x180|dmem=0xCB0 len=0x198|vi_width=1024|vi_width=512' \
  scratch/agent/s2067_task_abi_rows.log
rg -n '^\[CRASH\]|^\[ABORT\]' "$PORT" || true
git diff --check
```

The port is admissible only with both target VIs, live ABI and DMA-row
controls, no crash/abort before the harness SIGKILL, and a nonempty exact-span
join. Do not infer from a missing `0xE50/0x180` row or a zero payload without
those controls.
