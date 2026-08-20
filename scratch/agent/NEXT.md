# NEXT work unit (s2055)

HYPOTHESIS-ID: m5-callback-pcm-boundary

## Work unit

Ask the retail oracle for ground truth first, then make one build carrying a
paired PCM-boundary witness and run the qualified `11` route once. Keep forced
LLE, `LLE_UNGATED=1`, `LLE_SOLO=1`, C88=1, opt-in Factor 5 audio, spin yield,
the eleven width-640 Starts, the dense post-title schedule, and all existing
passive diagnostics fixed. Do not change the guest writer, audio task result,
callback behavior, or any guard.

The witness must report the same full byte span at both existing endpoints:
`ultramodern::queue_audio_buffer` before `audio_callbacks.queue_samples`, and
`queue_samples` on entry. Include phase/origin, RDRAM pointer, sample count,
full byte count (`sample_count * 2`), full-span FNV, and full-span nonzero byte
count. Use one phase-scoped ordinal per endpoint with the existing bounded
cadence. Preserve the existing task/gate controls as positive controls.

Because the concurrent four-process launch in s2054 crashed two arms in
`waitForAnyAudioSlot` and lost the fourth result while the uncontended retry
was valid, run this single witness arm without another game process.

## Competing hypotheses and discriminator

- **H-P — probe-unit false zero:** target-phase source and consumer rows pair
  on pointer/length and have equal full-span hashes/nonzero counts; the old
  `pcm-sanity` zero was caused by scanning a different sample/byte unit.
- **H-B — host boundary mutation:** a target-phase source row is nonzero, but
  the consumer row for the same pointer/length has a different or zero
  full-span hash.
- **H-T — callback/task boundary:** target-phase task and gate controls fire,
  but neither PCM endpoint has a row; the ABI/dispatch boundary is before the
  host callback.
- **H-Q — phase/join error:** source and consumer rows exist, but their
  pointer, length, ordinal, or phase/origin join is inconsistent; the prior
  title/H2 versus hangar/H4 split was attribution or queue timing rather than
  a uniform PCM boundary.

The single discriminator is the phase-keyed source/consumer table at title
VI `1024 @ 0x00790400` and hangar VI `512 @ 0x006AB400`, joined by full byte
count and pointer/hash, with live task/gate rows and the oracle's
whole-RDRAM/VI controls. A missing target row is admissible only when the
same-run task/gate positive controls fire.

## Commands

```sh
# Ground truth first.
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 55 --hit-cap 1 --watch-write 0x0:0x800000 \
  --watch-pc 0x800C28F0,0x800B47D0,0x8008E57C --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2055_oracle.log 2>&1

# Add the paired witness, export submodule patches if lib/ changes, then build.
cmake --build build --config Debug --target RogueSquadron64Recomp

route_keys='640@6:start 640@11:start 640@16:start 640@21:start 640@26:start 640@31:start 640@36:start 640@41:start 640@46:start 640@51:start 640@56:start 1024@2:a 1024@3:start 1024@4:a 1024@5:start 1024@7:a'
env REGRESS_SECS=90 REGRESS_INTERVAL=0.6 REGRESS_KEYS="$route_keys" REGRESS_LABEL=s2055_pcm_boundary \
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LOG_ALL=1 \
  ROGUESQ_LOG_M5_CALLER_EDGE=1 ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 \
  ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_VI_TRANSITION=1 \
  ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 \
  ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 \
  zsh tools/regress.sh scratch/agent/s2055_pcm_boundary 90 \
  > scratch/agent/s2055_pcm_boundary_driver.log 2>&1
```

Inspect the oracle control counts, the port `verdict.json`, preflight/phase
lines, target route markers, paired PCM rows, task/gate controls, and log tail.
