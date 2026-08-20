# NEXT work unit (s2004) — map audio DMA payloads to the AI/PCM bridge

HYPOTHESIS-ID: m5-audio-dma-pcm-contract

## Single work unit

Run the retail oracle positive control first, then add one batched host probe
to the existing phase-gated audio-task census. For every sampled
DMEM-to-RDRAM range, record a payload FNV hash, nonzero-byte count, first and
last nonzero byte, and the destination. In `ultramodern/src/audio.cpp`, record
the phase, RDRAM pointer, byte count, payload hash/nonzero count, and the
same buffer identity immediately before `queue_samples`. Keep the current
`musyx_stub`/`factor5_ucode_b` A/B only; do not enable another image, change a
guest gate, or add a skip/allow guard.

## Competing hypotheses and discriminating measurement

- **H-task-staging:** the candidate audio image receives malformed or wrongly
  staged input. Its treatment DMA payloads are zero or structurally invalid
  for PCM, or no stable output buffer is presented to the AI callback.
- **H-guest-buffer-selection:** the treatment creates nonzero PCM-like DMA
  payloads, but `osAiSetNextBuffer`/`queue_audio_buffer` points at a different
  or zero RDRAM range. This selects guest output-buffer routing or AI ordering.
- **H-bridge:** the same nonzero PCM-like destination and bytes reach the AI
  callback, but the callback-side samples/hash differ or `pcm-sanity` remains
  silent. This selects the host bridge rather than RSP/task staging.
- **H-audio-path-valid:** the treatment payload and AI buffer match and
  `pcm-sanity` becomes nonzero. This closes the current RSP/bridge boundary
  and moves the next unit to the remaining guest gate/scheduler behavior.

The discriminator is one phase-gated table joined by task row `n` and RDRAM
destination: DMA payload hash/nonzero count versus AI-buffer hash/nonzero
count versus `pcm-sanity`, with `[audtask-dispatch]` and the retail oracle as
positive controls. A null is unusable unless the whole-RDRAM oracle watch,
aligned `0x14974C` watch, task dispatch, and PCM callback controls all fire in
the same run.

## Ground-truth command before editing/building

```sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 45 --watch-write 0x0:0x800000 --watch-write 0x14974C:0x149750 --detail-watch 1 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start > scratch/s73_post_a_scene/m5-audio-step5-oracle.log 2>&1
```

Require nonzero whole-RDRAM and aligned-watch controls before interpreting
port nulls. Use only VI 1024/origin `0x00790400` and VI 512/origin
`0x006AB400` as phase gates.

## Exact probe/build/run sequence

1. Add the payload fields to the existing `rsp.cpp`/`rsp.hpp` audio-DMA scope
   and the AI-buffer fields to `ultramodern/src/audio.cpp`. Keep the existing
   row/range join key and phase budgets; batch all fields into this one build.
2. Run `./submodule-patches/export.sh` and build:

   ```sh
   cmake --build build --config Debug --target RogueSquadron64Recomp
   ```

3. Launch both arms concurrently from that one binary with the identical
   phase schedule:

   ```sh
   env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_SPBOOT=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step5-control 30 12
   env ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_SPBOOT=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step5-treatment 30 12
   ```

If concurrent control dies before VI 1024 as in s2003, retain that failure
as unevaluable and rerun the control standalone with the same binary before
interpreting the treatment rows; do not call the failed arm a null.
