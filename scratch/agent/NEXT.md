# NEXT work unit (s2053)

HYPOTHESIS-ID: m5-callback-pcm-witness

## Work unit

Run the retail oracle first with its whole-RDRAM positive control and the
title/hangar VI trace. Then run one bounded port recipe using the existing
qualified route: forced LLE, `ROGUESQ_LLE_UNGATED=1`,
`ROGUESQ_LLE_SOLO=1`, `ROGUESQ_SPIN_YIELD=1`, C88=1, opt-in audio, the eleven
width-640 Starts, the dense post-title schedule, and all passive audio bridge
and gate diagnostics. This is a callback-side witness experiment; do not
change the guest writer, AI shortcut, SDL callback, or any guard.

## Competing hypotheses and discriminator

- **H1 — upstream PCM is valid:** target-phase `[pcm-bridge]` rows have
  `nz>0` and target-phase `[pcm-sanity]` has `all_zero=0`.
- **H2 — the host callback/device boundary loses the samples:** target-phase
  `[pcm-bridge]` rows have `nz>0`, but `[pcm-sanity]` remains all-zero.
- **H3 — the audio task/ABI produces no payload:** target-phase bridge rows
  have `nz=0` while the task, gate, and queue controls are live.
- **H4 — the guest never submits/queues a target-phase buffer:** no target
  phase bridge row appears despite live `audtask-dispatch`, gate, and VI
  controls. Treat the result as guest submit/queue, not a device null.

The single discriminator is the phase-keyed join table at both target anchors:
`VI 1024/0x00790400` and `VI 512/0x006AB400`, joining `[audtask-dispatch]`,
`[m5-gate]`, `[pcm-bridge] nz/fnv`, and `[pcm-sanity] all_zero`. The oracle
whole-RDRAM count and port preflight/VI chain are positive controls; title
bridge rows must visibly fire in the same run before a target-phase null is
interpreted.

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
  > scratch/agent/s2053_oracle.log 2>&1

strings build/RogueSquadron64Recomp | rg -n 'ROGUESQ_SPIN_YIELD|site=menuInput|\[pcm-bridge\]'

set +e
route_keys='640@6:start 640@11:start 640@16:start 640@21:start 640@26:start 640@31:start 640@36:start 640@41:start 640@46:start 640@51:start 640@56:start 1024@2:a 1024@3:start 1024@4:a 1024@5:start 1024@7:a'
env REGRESS_SECS=180 REGRESS_INTERVAL=0.6 REGRESS_KEYS="$route_keys" REGRESS_LABEL=s2053_pcm_witness \
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LOG_ALL=1 \
  ROGUESQ_LOG_M5_CALLER_EDGE=1 ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 \
  ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_VI_TRANSITION=1 \
  ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 \
  ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_PCM_SANITY=1 zsh tools/regress.sh \
  scratch/agent/s2053_pcm_witness 180 > scratch/agent/s2053_pcm_witness_driver.log 2>&1
rc=$?
printf 'recipe_rc=%s\n' "$rc"
```

Inspect only `verdict.json`, `env.txt`, phase-keyed counts/joins for the four
marker classes, and log tails; do not read a full run log. If the harness
reports a late width-640 key without a new VI transition after the already
qualified VI 512, retain the target-phase rows and label only that late-key
check as a recipe-quality warning.
