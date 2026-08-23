# NEXT work unit (s2196) — compare osViSwapBuffer caller tables

HYPOTHESIS-ID: m5-a1-vi-swap-caller-parity

## Work unit

First obtain retail ground truth before adding the port instrument. Run the
oracle with its whole-RDRAM positive-control watch and `--watch-pc` on the
retail `osViSwapBuffer` symbol (`0x80035500`), while `--vi-trace` records the
live width/origin at each execution:

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 45 --hit-cap 10000 \
  --watch-write 0x0:0x800000 --watch-pc 0x80035500 \
  --first-watch 0 --vi-trace \
  > scratch/agent/s2196_retail_vi_swap_callers.log 2>&1
```

The oracle run must show at least 10,000 whole-RDRAM hits, positive
`osViSwapBuffer` execution rows, and 640 VI rows at both
`0x00696100` and `0x00696600`. Only then add one gated table to
`src/main/upstream_compat.cpp:osViSwapBuffer_recomp` and build once:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
```

The table is keyed by `ctx->r31 - 8` (the guest caller), framebuffer physical
argument, and the current host VI width/origin. It must include every caller
with a positive first-16-call control, then phase-scoped counts for the
qualified image/LLE recipe. Run the port once with the existing writer and
phase controls plus `ROGUESQ_LOG_VI_CALLERS=1`; kill it with SIGKILL after the
first-origin phase or the 180-second watchdog, whichever comes first. Parse
one table containing the caller/fb rows, `0x0066A500` and `0x00696100` phase
controls, the six writer rows, and any `0x00696600` phase.

## Competing hypotheses and discriminator

- H-RetailPortCallerParity: the retail caller/fb pair(s) observed at
  `0x00696600` also occur in the port table; the missing phase is downstream
  of the guest swap call.
- H-PortMissingSecondCaller: a retail second-origin caller/fb pair is absent
  from the port table; the guest dispatch/route does not reach that swap.
- H-PortWrongSwapArgument: the caller exists in both runs, but its port
  framebuffer argument maps to the first origin or another buffer.
- H-HostPhaseCommit: caller and framebuffer sequences match, but the port
  never publishes `0x00696600` through its host VI transition.
- H-CoverageFailure: either whole-RDRAM/oracle swap controls or the port
  first-origin controls are absent; reject the comparison as invalid.

The discriminator is the single retail/port caller-by-fb table, with positive
controls and phase rows in the same runs. A missing retail second-origin pair
selects H-PortMissingSecondCaller; a present caller with a wrong port fb
selects H-PortWrongSwapArgument; matching caller/fb rows with no port phase
select H-HostPhaseCommit; matching phase evidence selects
H-RetailPortCallerParity. Do not add a guard, task rewrite, writer filter, or
audio-default change.
