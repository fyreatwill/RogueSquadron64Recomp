# NEXT work unit (s2188) — retail writer identity census

HYPOTHESIS-ID: m5-a1-retail-writer-census

## Work unit

Ask the retail oracle which guest PCs write each of the six named physical
words. Use one run with the whole-RDRAM positive control, all six target
watches, per-target writer-PC histograms, and VI tracing. This is ground truth
work; do not rebuild the port or add a port instrument.

Exact command from the repository root (capture path has a non-dot final
component):

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
  --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2188_retail_writers.log 2>&1
```

Parse the whole-RDRAM removal/control, VI 640 rows at origins
`0x00696100`/`0x00696600`, each target hit count, and each target's PC
histogram into `scratch/agent/s2188_retail_writers.txt`. Require both the
whole-RDRAM and 640 controls before interpreting a target zero.

## Competing hypotheses and discriminator

- H-RetailWriterAllNamed: all six target watches have positive writes and
  their PC histograms identify the remaining writers.
- H-RetailWriterShared: the targets are written by one shared PC or a small
  known set, collapsing the five open writer identities.
- H-RetailWriterPhaseSplit: the writer histogram changes between the two 640
  origins, so target identity is phase-specific.
- H-RetailWriterCoverageFailure: the whole-RDRAM or 640 control is absent, or
  target watches are silent without a valid phase, so no writer conclusion is
  allowed.

The discriminator is one same-run table of whole-RDRAM control, VI phase,
target count, and per-target writer-PC histogram. It selects whether the
open identities are distinct, shared, phase-specific, or merely uncovered.
Do not add a port guard, disable `NAN_CHECK`, skip/allow cinematic loads, or
re-flip the image-arm default.
