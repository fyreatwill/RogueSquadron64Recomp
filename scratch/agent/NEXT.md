# NEXT work unit (s2177) — retail exec of dispatcher extract-frame jal

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

s2176 selected `H-NaNAbortInVec3Cross` on the queued
failing `=1` soak: last first-slot 87A0 n=5185 t=23.7 is
followed by 87A8 dest=`0x800CA748`, transform
entry+return, and dispatch n=325 return; dispatch n=326
then SIGABRTs in `vec3Cross` `NAN_CHECK` from
`0x800A8640` `jal 0x80059D18`. Hang hyps are refuted on
that soak. Do not enqueue `s2175_image_hang` again.

Ask ground truth before any port instrument or
`NAN_CHECK` change: does retail execute that jal / the
`vec3Cross` callee at cinematic 640/`0x00696100`?

Do not S32-address, NULL-skip, re-flip default-on,
skip/allow the lwc / transform / extract jal, disable
`NAN_CHECK`, add a wait/slot guard, or log `$t0`.
Oracle does not print FPRs; do not claim NaN/finite
from this run.

## Competing hypotheses and discriminator

- `H-RetailExecsJal8640`: same-run `[gpr-ctl]`, watch0
  10000, VI 640 including origin `0x00696100`, and
  exec `0x800A8640` n>=1 (and `0x80019548` n>=1).
- `H-RetailSkipsJal8640`: those controls fire;
  `0x800A8640` exec=0.
- `H-CoverageFailure`: missing `[gpr-ctl]`, watch0
  10000, or VI 640/`0x00696100`.

Positive controls: `[gpr-ctl]`; watch 0 write
callbacks=10000; `[vi]` 640 origin `0x00696100`.

## Exact commands

No game rebuild. Rice 45s, same recipe as s2172.

    tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
      --secs 45 --hit-cap 64 \
      --watch-write 0x0:0x800000 \
      --watch-pc 0x800A8640,0x80059D18,0x80059F10,0x80019548 \
      --first-watch 0 --vi-trace \
      > scratch/agent/oracle_s2177_vec3cross_pcs.log 2>&1

Table to `scratch/agent/s2177_vec3cross_pcs.txt`.
