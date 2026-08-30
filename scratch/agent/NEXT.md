# NEXT work unit — expose the scheduler consumed-message handoff

HYPOTHESIS-ID: scheduler-message-identity-target-phase

Run one independent retail-oracle capture at the adjacent scheduler receive
boundary. Session 3269 reached the target title and hangar phases and proved
`0x80019CD0` is live, but its exposed registers contain no accepted-message
identity. Add the immediately preceding PC and the supported field dump in
the same run to determine whether the message pointer/type is visible before
or after the receive handoff.

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
- `H-HandoffStillOpaque`: both adjacent PCs are live in target phases but the
  oracle still cannot expose a consumed message or type, so a new ground-truth
  boundary is required.

## Discriminator

The whole-RDRAM write watch must reach 10,000 hits and the run must reach the
retail title 1024 and hangar 512 gates. Watch both `0x80019CCC` and
`0x80019CD0` with detail, add `--pc-field-dump 0x80019CCC,0x80019CD0`, and
phase-gate target origins `0x00790400,0x00790800`. A target row exposing a
message pointer/type plus anomalous `89F/28D44` selects `H-SpMsgMutated`; a
valid non-type-2 row selects `H-OtherOsTask`; a valid target wall with an
accepted receive but no type-2 row selects `H-Type2AbsentAtRecv`. If both PCs
remain live but no message identity is exposed, select `H-HandoffStillOpaque`
and park this interface rather than repeating it.

## Exact command

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --secs 60 --watch-write 0x0:0x800000 \
  --watch-pc 0x80019CCC,0x80019CD0 --detail-watch 1 --detail-watch 2 \
  --pc-field-dump 0x80019CCC,0x80019CD0 \
  --pc-phase-log-width 0x00790400:1024 \
  --pc-phase-log-width 0x00790800:1024 \
  --vi-trace --hit-cap 256
```

Capture output under `scratch/agent/` with a non-dot final path. Do not build
or change port/audio behavior until the target-phase identity row is
classified.
