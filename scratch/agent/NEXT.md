# NEXT work unit (s872)

HYPOTHESIS-ID: m3-coalescer-phase-driver

Run one retail-oracle writer-attribution experiment at the newly identified
`runVideoFrameTick` boundary. Use the documented hangar-driving Start schedule
and physical watches on the caller globals (`0x1163e4:0x1163ec`) and free-list
head (`0x10ff18:0x10ff1c`). Preserve the whole-RDRAM, PIF, and VI positive
controls. Do not change the port or add instrumentation.

Competing hypotheses:

- H-retail-later-writer: after a post-320 VI transition, retail writes the
  caller globals or head at a later PC not present in the early-only census.
- H-retail-init-only: even after the transition, target writes remain confined
  to the early initialization PCs.
- H-driver-still-stalled: the schedule reaches PIF but never leaves width 320,
  so writer absence remains unevaluable rather than negative.

Discriminating measurement: whole-RDRAM, PIF, and VI controls must all fire;
VI must show a width/origin transition after 320. Only then classify target
watch PCs. A later target PC selects H-retail-later-writer; only early PCs
select H-retail-init-only for the reached phases; no post-320 transition is
H-driver-still-stalled and is not evidence about later writers.

Exact commands from the repo root:

```sh
tools/oracle/build/rs64_oracle \
  --core "$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib" \
  --rom "$PWD/rogue_squadron.z64" \
  --secs 70 --vi-trace --pif-trace \
  --watch-write 0x0:0x800000 \
  --watch-write 0x1163e4:0x1163ec --detail-watch 1 \
  --watch-write 0x10ff18:0x10ff1c --detail-watch 2 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,\
36:start,41:start,46:start,51:start,56:start --hold-ms 150
```

The ROM path must be verified before launch; if the repo-root copy is absent,
use `/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64`
without changing the experiment.
