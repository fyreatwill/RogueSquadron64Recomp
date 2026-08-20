# NEXT work unit (s2052)

HYPOTHESIS-ID: m5-title-to-hangar-route

## Work unit

Run the retail oracle first with its whole-RDRAM positive control and the
title/hangar VI trace. Then run one bounded port recipe using the existing
build and the previously hangar-capable LLE mode: retain forced LLE, add
`ROGUESQ_LLE_UNGATED=1` and `ROGUESQ_LLE_SOLO=1`, retain
`ROGUESQ_SPIN_YIELD=1`, C88=1, opt-in audio, the eleven width-640 Starts, and
the dense post-title schedule. This is a route-reproduction experiment, not
a guest-value or PCM experiment.

## Competing hypotheses and discriminator

- **H1 — the missing LLE mode gates the handoff:** preflight passes, title VI
  1024 occurs, `[slot-ret-caller] site=menuControllerInput` fires after that
  title anchor, `[spin-yield] site=menuInput` fires, and VI 512 follows.
- **H2 — the handoff is blocked independently of LLE mode:** title VI 1024
  and `menuInit` yield occur, but `menuControllerInput`, `menuInput` yield,
  and VI 512 remain absent.
- **H3 — the menu-input patch is not live:** title and
  `menuControllerInput` controls fire, but no `site=menuInput` spin marker or
  VI 512 appears. Check binary/fixup provenance before another route change.
- **H4 — input/visual qualification failed:** preflight or host Start control
  is absent. Discard the route result and request an active desktop run.

The single discriminator is the ordered positive-control chain:
`input=ok visual=ok` -> `menuInit` spin -> VI 1024 ->
`menuControllerInput after1024=1` -> `menuInput` spin -> VI 512. A PCM or
bridge row is still inadmissible unless the final VI 512 control fires.

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
  > scratch/agent/s2052_oracle.log 2>&1

set +e
route_keys='640@6:start 640@11:start 640@16:start 640@21:start 640@26:start 640@31:start 640@36:start 640@41:start 640@46:start 640@51:start 640@56:start 1024@2:a 1024@3:start 1024@4:a 1024@5:start 1024@7:a'
env REGRESS_SECS=180 REGRESS_INTERVAL=0.6 REGRESS_KEYS="$route_keys" REGRESS_LABEL=s2052_hangar_recipe \
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LOG_ALL=1 \
  ROGUESQ_LOG_M5_CALLER_EDGE=1 ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 \
  ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_VI_TRANSITION=1 \
  ROGUESQ_LOG_PCM_SANITY=1 zsh tools/regress.sh \
  scratch/agent/s2052_hangar_recipe 180 > scratch/agent/s2052_hangar_recipe_driver.log 2>&1
rc=$?
printf 'recipe_rc=%s\n' "$rc"
```

Confirm the executable contains `ROGUESQ_SPIN_YIELD` and the
`site=menuInput` marker before running. Inspect only `verdict.json`, `env.txt`,
bounded marker counts, and log tails; do not read a full run log.
