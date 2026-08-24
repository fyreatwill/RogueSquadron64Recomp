# NEXT work unit (s2207) — establish retail early-origin ground truth

HYPOTHESIS-ID: m5-a1-retail-early-origin-ground-truth

## Work unit

Run one independent retail-oracle phase census. Use the existing oracle
binary and retail ROM, with `--vi-trace` and the mandatory whole-RDRAM positive
control in the same run:

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 45 --watch-write 0x0:0x800000 --vi-trace \
  > scratch/agent/s2207_retail_early_origin.log 2>&1
```

Record the whole-RDRAM hit count, every 640-width origin in the trace, and
whether `0x0066A500` and/or `0x0066AA00` occurs. Do not build a new instrument,
change the VI default, add a port guard, rewrite a task, or change audio
dispatch. This is ground truth for the port's new early-prefix discrepancy.

## Competing hypotheses and discriminator

- H-RetailEarlyA500: retail emits `0x0066A500` but never `0x0066AA00`; the
  port's `0x0066AA00` is not a retail-grounded early phase.
- H-RetailEarlyAA00: retail emits both origins in one trace; `0x0066AA00` is
  legitimate and the port/logger discrepancy remains a route-selection
  question.
- H-RetailTraceCoverage: the oracle reaches a positive whole-RDRAM count but
  no 640 phase, so this run cannot classify either origin and the next probe
  must improve retail driving rather than interpret a null.

The discriminator is the same-run pair `(whole-RDRAM hit count, 640-origin
set)`: a positive control plus only `0x0066A500` selects H-RetailEarlyA500; a
positive control plus both origins selects H-RetailEarlyAA00; a positive
control with no 640 rows selects H-RetailTraceCoverage. A zero whole-RDRAM
count invalidates every phase conclusion.

## Exact commands

```sh
rg -n "whole-RDRAM|watch\]|\[oracle\] done|vi_width=640|0x0066A500|0x0066AA00" \
  scratch/agent/s2207_retail_early_origin.log
```
