# NEXT work unit (s2121) — oracle-first key-on early-return census

HYPOTHESIS-ID: m5-keyon-retail-ground-truth

## Work unit

Run one retail-oracle census for the complete eight-site `musyxKeyOnVoice`
divide/overflow early-return class before adding a port instrument or changing
any generated guard. Use the whole-RDRAM watch as the oracle positive control,
phase-gate interpretation on VI title/hangar coverage, and watch all eight
guest PCs in the same run. The class is:

    0x80090CEC, 0x80090D04, 0x80090D30, 0x80090D48,
    0x80090D74, 0x80090D8C, 0x80090DB8, 0x80090DD0

## Competing hypotheses and single discriminator

- `H-KeyOnRetailDead`: the guarded arithmetic sites are not reached by the
  retail hangar route; with whole-RDRAM and hangar controls positive, all eight
  `--watch-pc` sites remain at zero.
- `H-KeyOnRetailMixed`: retail reaches a strict subset of the class. The
  watched-PC hit set and each site's `exec-prev` predecessor identify the
  bounded site class for the next port audit; no other site may be changed.
- `H-KeyOnRetailLive`: retail reaches multiple or all eight sites in the
  covered hangar route. This proves the class is live, not that every divisor
  or descriptor is valid; the next step must still capture the operand contract
  before relaxing a guard.

The single discriminator is the complete watch table from this one run:
whole-RDRAM positive-control hits, VI title `1024 @ 0x00790400`, VI hangar
`512 @ 0x006AB400`, and per-site execution hits plus `exec-prev` attribution.
Zero site hits without both phase controls is unevaluable. Any nonzero subset
selects `H-KeyOnRetailMixed` and the exact subset; broad hits select
`H-KeyOnRetailLive`. No result authorizes a guard removal in this work unit.

## Exact command

Run from the repository root; capture only the oracle output:

    env tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
      --secs 75 --hit-cap 200 \
      --watch-write 0x0:0x800000 \
      --watch-pc 0x80090CEC,0x80090D04,0x80090D30,0x80090D48,0x80090D74,0x80090D8C,0x80090DB8,0x80090DD0 \
      --first-watch 0 --vi-trace \
      --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
      > scratch/agent/s2121_oracle_keyon.log 2>&1

Inspect the bounded `[watch]`, `[hit]`, `[vi]`, and `exec-prev` rows only.
Do not build or add a port diagnostic until this independent census has both
positive controls and a selected site set.
