# NEXT work unit — capture retail scheduler message identity at the receive boundary

HYPOTHESIS-ID: scheduler-message-identity-target-phase

Run one independent retail-oracle capture at the generated scheduler receive
call site. The selector region was zero-read even when widened, while the
pending-state and VI-boundary controls were live; move upstream to the
message that should publish the target-phase transition.

## Competing hypotheses

- `H-SpMsgMutated`: the target-phase accepted message is type `0x02` but its
  `89F/28D44` identity or payload is mutated.
- `H-OtherOsTask`: the target-phase message is valid but has a non-`0x02`
  task type, so the expected transition belongs to another task path.
- `H-Type2AbsentAtRecv`: the scheduler receive boundary has no accepted type-2
  target row despite valid receive activity.
- `H-RecvWatchUnavailable`: the receive watch lacks a target-phase row or its
  detail fields cannot be correlated, leaving all three semantic hypotheses
  unresolved.

## Discriminator

The whole-RDRAM write watch must reach 10,000 hits and the run must reach the
retail title 1024 and hangar 512 gates. Watch `0x80019CD0` with detail and
phase-gate the target origins `0x00790400,0x00790800`; retain the scheduler
identity fields and `89F/28D44` census in the same run. A target row with type
`0x02` and an anomalous identity selects `H-SpMsgMutated`; a valid target row
with another type selects `H-OtherOsTask`; a valid target wall with accepted
receive activity but no type-2 row selects `H-Type2AbsentAtRecv`. Missing or
uncorrelated target coverage selects `H-RecvWatchUnavailable`.

## Exact command

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --secs 60 --watch-write 0x0:0x800000 \
  --watch-pc 0x80019CD0 --detail-watch 1 \
  --pc-phase-log-width 0x00790400:1024 \
  --pc-phase-log-width 0x00790800:1024 \
  --vi-trace --hit-cap 256
```

Capture output under `scratch/agent/` with a non-dot final path. Do not build
or change port/audio behavior until the target-phase identity row is
classified.
