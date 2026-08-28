# NEXT work unit (s2949) — retail route message/branch ground truth

HYPOTHESIS-ID: m5-route-qualification-repair

## Context

s2948 added a regeneration-owned full-input probe at `0x80019CD8`. The fixed
port run emitted 771 rows, and its same-run `[f5-fetch-control]` positive
control fired 8 times. The route still stopped at pre-title VI 640
(`0x0066A500`), so the accepted retail tuple and message branch remain
unknown.

## Competing hypotheses and discriminator

- H-PrepareFieldBad: one route-preparation input differs between retail and
  port.
- H-PrepareTimingBad: the input tuple matches, but phase-relative ordering or
  timing differs.
- H-PrepareLogicBad: generated control flow differs at the scheduler boundary.

Run the retail oracle at `0x80019CD8` in title and hangar phases, retaining the
whole-RDRAM positive control. Compare the target-phase GPR/message/branch tuple
against s2948's port table. A named differing field selects Field or Timing;
matching inputs with different control flow selects Logic; absent target rows
invalidate the oracle run and select nothing.

## Exact work

From the repo root, run:

```sh
tools/oracle/build/rs64_oracle \
  --core ~/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom ~/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 180 --watch-write 0x0:0x800000 --watch-pc 0x80019CD8 \
  --pc-phase-log 0x00790400,0x006AB400 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
```

Capture to `scratch/agent/s2949_retail_route_message/`. If the existing oracle
cannot expose the message byte/branch, add that one ground-truth field in the
same unit; do not build a new port probe first.
