# NEXT work unit — retail source-span ground truth

HYPOTHESIS-ID: m5-retail-source-span-ground-truth

Session 3412 port result: both phase-qualified arms completed; `0x800078EC`
ran on the joined hangar route but wrote only zero bytes into the source span,
and stage 3 copied zero DMEM to `0x801798B0`. The next unit must establish the
retail value at the same physical span before any new port instrumentation.

Competing hypotheses and discriminating measurement:

- H-RetailSourceNonzero: retail writes nonzero bytes in the corresponding
  hangar source span from `0x800078EC`; nonzero post-store samples select this.
- H-RetailSourceZero: retail reaches the producer but all corresponding
  post-store samples are zero; this selects a shared legitimate-zero/input
  explanation over a port-only producer gap.
- H-RetailProducerAbsent: controls pass, but no producer or span writes occur in
  the hangar bucket; this selects a route or attribution mismatch and requires
  a new discriminator.

The single discriminator is one retail-oracle run with whole-RDRAM positive
control, title/hangar VI gates, `--watch-write 0x1797B0:0x179A48`,
`--watch-pc 0x800078EC`, phase logging for origin `0x006AB400`, and post-store
sampling for `0x800078EC`. Require complete controls and a hangar-bucket
payload histogram before classifying.

Exact commands:

1. `mkdir -p scratch/agent/s3413_retail_source_span && tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 120 --watch-write 0x0:0x800000 --watch-write 0x1797B0:0x179A48 --watch-pc 0x800078EC --pc-phase-log 0x006AB400 --post-value-pc 0x800078EC > scratch/agent/s3413_retail_source_span/oracle.log 2>&1`
2. Check whole-RDRAM, title/hangar, producer execution, and span/post-value
   summaries; classify only if all controls and the hangar bucket are present.
