# NEXT work unit (s2058)

HYPOTHESIS-ID: m5-service-store-edge

## Work unit

Use the already-built binary and the existing regeneration-stable s2028
census for one phase-keyed hangar input arm. Add Start presses only after VI
512 is live, so the run tests whether a later shutdown call follows the
worker's status-zero store. Do not add instrumentation, force a status byte,
add a skip, or change the retail writer.

## Competing hypotheses and discriminator

- **H-RetReturn — shutdown returns:** a 512-phase Start control triggers a
  later shutdown call after the phase-10 `0x03 -> 0x00` service store, and the
  matching `shutdown-entry` is followed by `shutdown-exit`.
- **H-Stall — shutdown waits:** the Start control and shutdown entry are live,
  but status 3 persists or no matching shutdown exit follows the store.
- **H-NoTrigger — input does not drive shutdown:** the 512-phase host/SDL
  controls do not fire or no shutdown entry follows them, so the run cannot
  test the return boundary.
- **H-JoinGap — event join is insufficient:** input, store, and shutdown
  controls all fire, but the phase/ordinal ordering cannot distinguish a
  post-store return from an earlier shutdown call.

The discriminator is one ordered table, phase-gated at VI 512:
`[pad-host]/[pad-sdl]` key control -> s2028 `service-store` with
`old=0x03,value=0` -> later `shutdown-entry` -> `shutdown-exit`, with
`shutdown_call` and event sequence. H-RetReturn requires the exit after the
store; H-Stall requires a post-store entry without exit or persistent status
3; H-NoTrigger is selected only when the input/shutdown positive control is
absent; H-JoinGap is selected only when all controls fire but the join cannot
order them. The title VI 1024, hangar VI 512, s2020 service entry/exit,
s2008 status writer, audio-task/ABI, and PCM source/consumer rows are same-run
positive controls.

## Commands

```sh
# Ground truth first: retail writer/status controls and target route.
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 55 --hit-cap 1 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x154620:0x154624 \
  --watch-pc 0x8009B5A8,0x8009B8A0,0x8009B7EC,0x8009B2C4 \
  --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start \
  > scratch/agent/s2058_oracle.log 2>&1

route_keys='640@6:start 640@11:start 640@16:start 640@21:start 1024@2:a 1024@3:start 1024@4:a 1024@5:start 1024@7:a 512@5:start 512@10:start 512@15:start 512@20:start 512@30:start 512@40:start'
env REGRESS_REQUIRE_VISUAL=1 REGRESS_SECS=180 REGRESS_INTERVAL=0.6 REGRESS_KEYS="$route_keys" REGRESS_LABEL=s2058_m5_shutdown_return \
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LOG_ALL=1 \
  ROGUESQ_LOG_S2028_A11=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2058_m5_shutdown_return 180 \
  > scratch/agent/s2058_m5_shutdown_return_driver.log 2>&1
```

Inspect oracle controls first. In the port log, require the 512-phase input
control and both target VIs before reading the ordered service/shutdown rows.
Use SIGKILL only if the harness does not clean up; do not interpret a missing
post-store return without a live shutdown-entry control.

ORIGIN: no guest writer, value, wait, guard, skip, audio task, callback, or default behavior changes; this is an input/ordering experiment using existing diagnostics.
