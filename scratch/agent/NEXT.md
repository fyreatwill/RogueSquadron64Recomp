# NEXT work unit (long oracle phase reachability)

HYPOTHESIS-ID: m3-postsec2-lle-control

s767 proved with corrected PIF tracing that scheduled Start reaches the retail
game (`0x7C4=0x10000000`), while a 25-second run still remained at VI width 320.
The next unit is the longer phase-gated oracle run, not a port build or target
watch.

## Competing hypotheses

- H-retail-reaches-phases: PIF-delivered Start produces the documented 640,
  1024, and/or 512 VI transitions during the long schedule.
- H-retail-320-only: PIF-delivered Start is visible, but this ROM/config still
  remains at 320, indicating a phase/timing or configuration divergence.
- H-retail-input-timing: PIF Start is visible but the schedule's timing misses
  the game's input windows; a shifted/repeated schedule is required.

## Discriminating measurement

Run the oracle with the corrected `--pif-trace`, `--vi-trace`, a whole-RDRAM
positive control, and the documented 11-entry Start schedule. PIF Start words
plus 640/1024/512 transitions select H-retail-reaches-phases; PIF Start words
with 320-only select H-retail-320-only; missing PIF Start at a press window
selects H-retail-input-timing. The positive control must fire in the same run.

## Command

    tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --secs 70 --pif-trace --vi-trace --watch-write 0x0:0x800000 \
      --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start

Record PIF button words, positive-control hit count, and VI transitions. Keep
the corrected oracle trace source/build; do not revert the `w0 || w1` trigger.

ORIGIN for the s767 oracle fix: PIF trace output previously checked only `w1`;
the button word is observed as `0x10000000` in `0x7C4`.
