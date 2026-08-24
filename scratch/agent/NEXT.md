# NEXT work unit (s2234) — exact retail PCM/task-output attribution

HYPOTHESIS-ID: m5-audio-image-contract

## Work unit

Run one retail-oracle capture with Rice video and the qualified Start schedule.
Arm the whole-RDRAM positive control first, then watch the exact PCM ring from
the port logs and the `data_ptr+0x100` task-data output span. Request
post-target rows for the recurring retail writer PCs found in s2233. Do not
change runtime code, generated output, task fields, gates, waits, guards, the
audio default, or the port image arm.

## Competing hypotheses and discriminating measurement

- **H-RetailPCMDirect:** the retail game writes the exact PCM ring during the
  title/hangar gate, with nonzero post-target values and writer PCs that can
  be joined to the port's image/PCM boundary.
- **H-RetailTaskOutput:** retail writes the task-data output span but not the
  exact PCM ring in the target phase; the missing edge is between image output
  and the consumer ring.
- **H-RetailOtherOutput:** neither exact watch has a target-phase output row;
  the broad-span writes in s2233 came from unrelated structures or consumers.
- **H-NoTargetRoute:** the oracle does not reach the driven 640 target, title
  `1024`, and hangar `512`, so a narrow null is unevaluable.

The discriminator is one run containing watch 0 over all RDRAM and both exact
watches. Watch 0 must reach its 10,000-callback positive-control threshold and
be removed before the other watches are interpreted. The run must reach
`640 @ 0x00696100`/`0x00696600`, title `1024 @ 0x00790400`, and hangar
`512 @ 0x006AB400`. A nonzero target-phase row on the PCM-ring watch selects
H-RetailPCMDirect; task-span-only rows select H-RetailTaskOutput; no exact
target-phase row selects H-RetailOtherOutput. Failure to reach the route
selects H-NoTargetRoute. No runtime change follows from any null.

## Exact command

Run from the repository root; the oracle drives retail and exits after the
capture. The first watch is deliberately whole RDRAM.

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 75 --hit-cap 200 --vi-trace \
  --watch-write 0x0:0x800000 \
  --watch-write 0x166450:0x169450 \
  --watch-write 0x171F70:0x173DB4 \
  --first-watch 0 --pc-hist-watch 1 --pc-hist-watch 2 \
  --post-value-watch 1 --post-value-watch 2 \
  --post-value-pc 0x80090f8c,0x80090fc0,0x80090fdc,0x80091000,0x80091078,0x800910ec,0x800910f8,0x8009114c,0x80091168,0x80091170,0x80091204 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2234_retail_exact_output.log 2>&1
```

Read only bounded results:

```sh
log=scratch/agent/s2234_retail_exact_output.log
grep -a -n -E 'positive-control threshold|^\[oracle\] done:|watch write |post-target-row-final|post-target-summary|post-value watch=|writer-pc watch=' "$log" | tail -160
grep -a -n -E '^\[vi\].*WIDTH 320 -> 640|^\[vi\].*WIDTH 640 -> 1024|^\[vi\].*WIDTH 1024 -> 512' "$log"
```
