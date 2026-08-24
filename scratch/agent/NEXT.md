# NEXT work unit (s2233) — retail-attributed image-output boundary

HYPOTHESIS-ID: m5-audio-image-contract

## Work unit

Run one retail-oracle capture with Rice video, the qualified Start schedule,
the whole-RDRAM positive control first, and a physical watch over the port's
Factor 5 image-stage/PCM destination span. Attribute writer PCs and post-store
values by target phase. This is the ground-truth checkpoint for s2232's
provisional, single-source H-ContractGap selection. Do not change runtime
code, generated output, task fields, gates, waits, guards, the audio default,
or the port image arm.

## Competing hypotheses and discriminating measurement

- **H-RetailImageWritesSame:** retail writes the watched output span in the
  target route, with writer PCs/payloads and ordering compatible with the port
  image stage and PCM consumers.
- **H-RetailUsesOtherOutput:** retail reaches the route but writes a different
  destination or uses a different output consumer; the port's stage-only rows
  are a real contract mismatch, not a missing guard.
- **H-PortOnlyPCM:** the nonzero port PCM rows come from an unrelated CPU/MORT
  or stale-buffer path; retail has no matching writes in the watched span.
- **H-NoTargetRoute:** the oracle fails to reach 640 target/title/hangar; any
  narrow null is unevaluable even if the whole-RDRAM control fires.

The discriminator is one oracle run containing both watches: watch 0 must show
the whole-RDRAM positive control, and watch 1 (`0x166000:0x17A000`) must report
phase-tagged writes, writer PCs, post-store values, and final nonzero/hash
state. Reaching `640 @ 0x00696100`, title `1024 @ 0x00790400`, and hangar
`512 @ 0x006AB400` is also required. A matching retail writer/value/order row
selects the next contract edge; a different destination selects a mapping
edge; no target route selects H-NoTargetRoute and requires a route recipe
review. No runtime change follows from a null or from a gate/guard hit.

## Exact commands

Run from the repository root; the oracle itself drives retail and exits after
the capture. The first watch is deliberately whole RDRAM and must remain in
the same run as the narrow watch.

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 75 --hit-cap 200 --vi-trace \
  --watch-write 0x0:0x800000 \
  --watch-write 0x166000:0x17A000 \
  --first-watch 0 --pc-hist-watch 1 --post-value-watch 1 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2233_retail_image_contract.log 2>&1
```

Read only bounded results:

```sh
log=scratch/agent/s2233_retail_image_contract.log
grep -a -c '^\[hit\].*watch=0\|^\[first-watch\].*0' "$log" || true
grep -a -c '^\[hit\].*watch=1\|^\[first-watch\].*1' "$log" || true
grep -a '^\[oracle\]\|^\[vi\].*width=\(640\|1024\|512\)' "$log" | tail -30
grep -a -E 'watch 1|watch=1|post-value|pc-hist|writer|final' "$log" | tail -40
```
