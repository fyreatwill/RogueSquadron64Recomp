# NEXT work unit (s2189) — phase-bucketed retail writer census

HYPOTHESIS-ID: m5-a1-retail-writer-census

## Work unit

Make one bounded oracle-only change: add repeatable phase buckets to the
writer-PC histogram, keyed by VI width 640 and origin. The existing
repeatable `--pc-hist-watch` support is already in place. Each configured
phase bucket must count the same six target watches independently, and the
shutdown table must print one histogram per phase and target. Do not rebuild
or instrument the port.

Build the oracle once:

```sh
tools/oracle/build.sh
```

Then run one same-run table from the repository root. The new option planned
for this work unit is repeatable `--pc-hist-phase ORIGIN`:

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 45 --hit-cap 10000 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x25A580:0x25A584 \
  --watch-write 0x0CA748:0x0CA74C \
  --watch-write 0x0C7B0C:0x0C7B10 \
  --watch-write 0x165E40:0x165E44 \
  --watch-write 0x0CDB58:0x0CDB5C \
  --watch-write 0x2231EC:0x2231F0 \
  --first-watch 0 \
  --pc-hist-watch 1 --pc-hist-watch 2 --pc-hist-watch 3 \
  --pc-hist-watch 4 --pc-hist-watch 5 --pc-hist-watch 6 \
  --pc-hist-phase 0x00696100 --pc-hist-phase 0x00696600 \
  --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2189_retail_writers_phase.log 2>&1
```

Parse the whole-RDRAM control, 640 row count at each configured origin,
six total target counts, and every phase/target histogram into
`scratch/agent/s2189_retail_writers_phase.txt`. Require both positive
controls before interpreting any phase bucket.

## Competing hypotheses and discriminator

- H-PhaseStable: both 640 origins contain the same writer set for each
  target; the cinematic phase is not writer-origin-specific.
- H-PhaseSplit: at least one target's writer PCs differ between
  `0x00696100` and `0x00696600`; attribution is phase-specific and becomes
  the next ground-truth discriminator.
- H-Target4Broad: the sparse targets stabilize but `0x165E40` remains broad
  in both buckets, so its 123-PC class needs a different boundary.
- H-PhaseCoverageFailure: whole-RDRAM or 640 controls fail, or configured
  buckets have no VI rows; no writer conclusion is allowed.

The discriminator is one same-run table of controls, phase-row counts, and
per-phase/per-target PC histograms. It selects stable attribution, a
phase-specific split, a target-4-only boundary, or invalid coverage.
