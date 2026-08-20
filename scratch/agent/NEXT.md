# NEXT work unit (s2059)

HYPOTHESIS-ID: m5-service-store-edge

## Work unit

Run one qualified forced-LLE/audio/C88=1 arm that leaves hangar input idle
until well after the worker's status-3 `0x03 -> 0x00` store should have
occurred, then sends one Start. Do not add instrumentation, force a status
byte, add a skip, change the retail writer, or change the scorer. The prior
s2058 key reached shutdown call 3 while status was still `0x02`, so its stall
was a pre-store result.

## Competing hypotheses and discriminator

- **H-PostStoreReturn** — the delayed Start produces a shutdown entry after
  the named service store, followed by a shutdown exit.
- **H-PostStoreStall** — the named store precedes shutdown entry, but status 3
  persists and no matching shutdown exit follows.
- **H-PreStoreAgain** — shutdown entry still precedes the named store, showing
  that the delayed input did not allow the worker edge to become live first.
- **H-NoStore** — the hangar service/status positive controls fire, but no
  `0x03 -> 0x00` store occurs before the delayed shutdown; this leaves the
  worker edge nondeterministic at this recipe and does not select a return.

The discriminator is one ordered, phase-10 table:
`service-store old=0x03 value=0` -> later `shutdown-entry` ->
`shutdown-exit`, with `shutdown_call`, thread, slot, and status on every edge.
H-PostStoreReturn requires the exit after the store; H-PostStoreStall requires
the post-store entry with persistent status 3 and no exit; H-PreStoreAgain is
selected only when the entry precedes the store; H-NoStore is selected only
when the service/status positive controls fire but the store is absent. Title
VI 1024, hangar VI 512, phase-10 `[pad-host]` input, s2020 service entry/exit,
s2008 writer, audio-task/ABI, and PCM source/consumer rows are same-run
positive controls.

The generic regress scorer may flag the stationary 512 phase because a
shutdown stall does not require a VI transition. Treat that check as
inapplicable only after the direct 512 `[pad-host]` and shutdown-entry
controls fire; do not accept a run with missing controls.

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
  > scratch/agent/s2059_oracle.log 2>&1

route_keys='640@6:start 640@11:start 640@16:start 640@21:start 1024@2:a 1024@3:start 1024@4:a 1024@5:start 1024@7:a 512@120:start'
env REGRESS_REQUIRE_VISUAL=1 REGRESS_SECS=240 REGRESS_INTERVAL=0.6 REGRESS_KEYS="$route_keys" REGRESS_LABEL=s2059_m5_post_store_shutdown \
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LOG_ALL=1 \
  ROGUESQ_LOG_S2028_A11=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2059_m5_post_store_shutdown 240 \
  > scratch/agent/s2059_m5_post_store_shutdown_driver.log 2>&1
```

Inspect the oracle controls first. In the port log, require both target VIs,
the delayed 512-phase input, and shutdown-entry before ordering the service
store and shutdown rows. Use SIGKILL only if the harness does not clean up.

ORIGIN: no guest writer, value, wait, guard, skip, audio task, callback, or
default behavior changes; this is an input/ordering experiment using existing
diagnostics.
