# NEXT work unit — repair retail phase attribution

HYPOTHESIS-ID: m5-earlier-producer-contract

The s3393 exact target census is closed as non-discriminating: the oracle's
whole-RDRAM and exact target watches fired, but its single 0x006AB400:512
writer histogram bucket reported no phase rows. Do one oracle-only repair
experiment before another port run. Keep the whole-RDRAM positive control and
the exact target-span watch, and batch both candidate 512-width VI origins in
the same run.

Competing hypotheses:

- `H-OriginIs006AB000`: target writes occur during the 512-wide VI bucket at
  origin `0x006AB000`; the earlier `0x006AB400` bucket was mis-keyed.
- `H-OriginIs006AB400`: the target writes belong to `0x006AB400`, and the zero
  histogram is an oracle phase-attribution bug unrelated to origin choice.
- `H-TargetOutside512`: target writes occur outside both candidate 512-wide
  buckets; phase attribution cannot identify a producer from this route.

Discriminator: with exact target-watch and whole-RDRAM controls both live, a
nonzero writer histogram in only one candidate bucket selects its origin;
nonzero rows in both indicate the phase key is not exclusive; zero rows in
both makes this attribution path unevaluable and ends this exact oracle-field
line of inquiry. Do not change port output or audio behavior in this unit.

Exact command:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 120 --watch-write 0x0:0x800000 --watch-write 0x1798B0:0x179A48 --watch-pc 0x800078E8,0x800078EC --pc-phase-log-width 0x006AB000:512 --pc-phase-log-width 0x006AB400:512 --pc-hist-watch 1 --pc-hist-phase 0x006AB000:512 --pc-hist-phase 0x006AB400:512 --vi-trace --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' --hold-ms 150 > scratch/agent/oracle_s3394_dual_origin.log 2>&1

Inspect only summary markers: whole-RDRAM count, target-span count, both
`writer-pc-phase` buckets, and the final VI phase counts. If either positive
control is absent, record the run as invalid instead of selecting a
hypothesis.
