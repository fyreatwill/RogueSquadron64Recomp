# NEXT work unit (s2066)

HYPOTHESIS-ID: m5-audio-image-output-contract

## Work unit

Run one phase-gated live task/value crosswalk using the existing qualified
route and existing audio probes; do not add instrumentation, regenerate, or
change task fields, dispatch, guards, or guest behavior. Ground truth comes
first: run the retail oracle with a whole-RDRAM positive control and the
candidate audio-output band watch, then run the port with the existing
`[audtask-abi]` and `[audtask-dma-range]` rows. Extract only target-phase rows
for the exact generated spans `dmem=0xE50 len=0x180` (`L_1E48`) and
`dmem=0xCB0 len=0x198` (`L_1314`), joining each to its task's
`output_buff`, `yield_data_ptr`, and `data_ptr` intervals.

## Competing hypotheses and discriminator

- **H-ImageOutputField** — one of the two generated write spans overlaps the
  live OSTask `output_buff` or `yield_data_ptr`, and the oracle's qualified
  writer watch attributes the same physical destination to the retail audio
  path.
- **H-ImageDataStruct** — neither span is an OSTask output field, but its
  DMEM-derived destination is within the task-data structure reached from
  `data_ptr`, with matching retail writer ownership.
- **H-ImageTaskAbiMismatch** — the generated destination overlaps none of the
  task's output/yield/data intervals, or its offset/length disagrees with the
  corresponding live task layout; the canary is then an ABI/staging defect.
- **H-OutputRouteUnevaluable** — the port rows, target phase, or oracle
  positive control is missing, so no field relationship is admissible.

The discriminator is one joined table keyed by task row and phase:
`dmem,len`, effective RDRAM span, `output_buff` interval,
`yield_data_ptr` interval, `data_ptr` interval, all three overlap flags,
`exit/canary`, and the oracle writer-PC hits for the same physical span.
`output/yield` overlap plus matching retail ownership selects
H-ImageOutputField; data-only overlap plus matching ownership selects
H-ImageDataStruct; a complete no-overlap/offset mismatch selects
H-ImageTaskAbiMismatch; any missing control or row selects
H-OutputRouteUnevaluable.

## Exact commands

Run the retail witness before the port run. The whole-RDRAM watch is watch 0;
the candidate band is watch 1. Accept oracle evidence only if the positive
control fires, the `0x166000..0x17A000` band watch fires, and the driven
run reports title VI 1024 and hangar VI 512 at the hangar origin.

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 60 --vi-trace --pif-trace \
  --watch-write 0x0:0x800000 \
  --watch-write 0x166000:0x17A000 \
  --first-watch 1 --pc-hist-watch 1 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start

env GAME_EXTRA_ENV='ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1' \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s2066_task_abi 60 12

PORT=scratch/s73_post_a_scene/s2066_task_abi/run.log
rg '^\[(phase|audtask-abi|audtask-dma-row|audtask-dma-range)\]' "$PORT" \
  > scratch/agent/s2066_task_abi_rows.log
rg -n 'dmem=0xE50 len=0x180|dmem=0xCB0 len=0x198|vi_width=1024|vi_width=512' \
  scratch/agent/s2066_task_abi_rows.log
git diff --check
```

The port is admissible only with both target VIs, live `[audtask-abi]` and
`[audtask-dma-row]` controls, and no crash/abort. Do not infer from a missing
DMA row or a zero payload without those controls.
