# NEXT work unit (s2223) — phase-keyed retail key-on guard table

HYPOTHESIS-ID: m5-audio-keyon-contract

## Work unit

Extend the oracle's range-PC phase logger so it accepts an explicit
`ORIGIN:WIDTH` bucket, then run one Rice-driven retail census with the existing
whole-RDRAM positive control, the two target 640 buckets, and a new
`0x006AB400:512` hangar bucket. Keep the range watch over
`0x80090A3C:0x80090E04`; summarize the eight transfer PCs immediately before
the skipped divide spans and the eight previously watched divide PCs, including
`$v0/$s1/$a0/$a2` at each transfer PC. Do not build the port or remove/change a
key-on return in this unit.

Competing hypotheses and the single discriminator:

- H-RetailPhaseInvariantGuard: all eight divide PCs remain zero at both target
  origins and hangar, while all eight transfer PCs execute; their register
  tuples stay equivalent across phases. The port's four observed divides are a
  port/retail contract difference.
- H-RetailHangarDivides: at least one of the eight divide PCs executes in the
  512 hangar bucket. The target-only null was not the hangar contract.
- H-RetailBranchStateShift: retail still skips every divide in all buckets, but
  one or more transfer-PC register tuples change between target and hangar.
  The next comparison is the branch-tested state, not a missing PC watch.
- H-PhaseCoverageFailure: the new hangar range bucket is empty despite a
  positive whole-RDRAM control and a positive `512 @ 0x006AB400` VI row; no
  branch or operand conclusion is allowed.

The discriminator is one phase-keyed matrix: for each of the three phase
buckets, counts for the eight transfer PCs and eight divide PCs, plus the
transfer-PC `$v0/$s1/$a0/$a2` value sets. A nonzero hangar divide selects
H-RetailHangarDivides; zero divides with invariant tuples select
H-RetailPhaseInvariantGuard; zero divides with changed tuples select
H-RetailBranchStateShift; missing controls select H-PhaseCoverageFailure.

## Exact commands

1. Add `--pc-phase-log-width ORIGIN:WIDTH` to `tools/oracle/rs64_oracle.c`,
   preserving the existing 640-only `--pc-phase-log` behavior and making the
   new bucket print the same range-PC rows. Build with:

~~~sh
bash tools/oracle/build.sh
~~~

2. Run from the repository root:

~~~sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 60 --vi-trace --status-poll \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --watch-write 0x0:0x800000 \
  --watch-pc-range 0x80090A3C:0x80090E04 \
  --pc-phase-log 0x00696100 --pc-phase-log 0x00696600 \
  --pc-phase-log-width 0x006AB400:512 --hit-cap 25 \
  > scratch/agent/s2223_retail_keyon_guard_table.log 2>&1
~~~

Required controls: `positive-control threshold reached`, whole-RDRAM writes at
least 10,000 with removal `rc=0`, repeated 640 rows at both target origins,
and a `512 @ 0x006AB400` row. Use `rg '^\\[hit\\]'` plus an awk phase matrix;
do not infer branch semantics from counts without the transfer-PC register
tuples.
