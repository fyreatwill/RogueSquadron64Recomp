# NEXT work unit (s2208) — drive retail through the early 640 phase

HYPOTHESIS-ID: m5-a1-retail-early-origin-ground-truth

## Work unit

Run one independent retail-oracle phase census using the documented Rice
video plugin and verified Start schedule. Keep the mandatory whole-RDRAM
positive control and `--vi-trace` in the same run. The previous undriven
recipe stopped at boot 320, so this is a coverage repair, not a port change.

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --hold-ms 150 --secs 120 --watch-write 0x0:0x800000 --vi-trace \
  > scratch/agent/s2208_retail_early_origin_rice.log 2>&1
```

Record the positive-control count, every `width=640` origin, and whether
`0x0066A500` and/or `0x0066AA00` occurs. Do not build a new instrument,
change the VI default, add a port guard, rewrite a task, or change audio
dispatch.

## Competing hypotheses and discriminator

- H-RetailEarlyA500: the driven retail trace reaches width 640 and includes
  `0x0066A500` but never `0x0066AA00`; the port's quiet `0x0066AA00` is not a
  retail-grounded early phase.
- H-RetailEarlyAA00: the driven retail trace includes `0x0066AA00` (with or
  without `0x0066A500`); the port's quiet origin is retail-grounded and the
  discrepancy remains a route-selection question.
- H-RetailOther640: the positive-control run reaches width 640, but neither
  named early origin occurs; the driver reaches a different retail phase and
  the schedule needs a narrower phase discriminator.
- H-RetailTraceCoverage: the positive control passes but no width-640 row
  occurs; Rice/input driving still did not reach the comparable route.

The discriminator is the same-run pair `(whole-RDRAM hit count, 640-origin
set)`. A zero whole-RDRAM count invalidates every phase conclusion.

## Exact commands

```sh
rg -n "^\\[vi\\]|positive-control|\\[oracle\\] done|vi-swap-phase|0x0066A500|0x0066AA00" \
  scratch/agent/s2208_retail_early_origin_rice.log
```
