# NEXT work unit (s957)

Run a two-arm retail-oracle input/phase control before retrying the callback-
table watch. Launch undriven and named-`start` arms concurrently, each with a
whole-RDRAM positive control, `--vi-trace`, `--vi-poll`, and `--pif-trace`; do
not interpret callback-table zeros from either arm. No build or generated-code
edit is needed.

HYPOTHESIS-ID: m3-slotdispatcheriter-stacksp-class

Competing hypotheses:

- H-oracle-config-mapping: driven PIF state differs from the named-`start`
  expectation while the undriven arm follows the normal phase timeline.
- H-oracle-core-phase: both arms remain at VI 320 despite live controls.
- H-oracle-undriven-timeline: both arms progress identically and reach the
  documented transition only after a longer interval.
- H-oracle-callback-unclassified: driven arm crosses VI 320 while its PIF
  state is accepted, but the callback watch remains zero.

Discriminating measurement: compare PIF words and VI width/origin in the two
arms. A driven Start PIF transition plus VI > 320 selects input acceptance;
both arms at VI 320 selects core/setup; identical delayed progress selects
timeline; driven VI > 320 with zero callback hits selects callback-unclassified.
The whole-RDRAM watch must visibly fire in both arms.

Exact starting commands (create the result directory first):

`mkdir -p scratch/agent/oracle_results/s957_oracle_phase`

`tools/oracle/build/rs64_oracle --configdir /Users/williambuckley/Documents/Tools/rs64-oracle/cfg --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 60 --watch-write 0x0:0x800000 --hit-cap 200 --vi-trace --vi-poll --pif-trace > scratch/agent/oracle_results/s957_oracle_phase/undriven.log 2>&1 &`

`tools/oracle/build/rs64_oracle --configdir /Users/williambuckley/Documents/Tools/rs64-oracle/cfg --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 60 --watch-write 0x0:0x800000 --hit-cap 200 --vi-trace --vi-poll --pif-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 > scratch/agent/oracle_results/s957_oracle_phase/driven.log 2>&1 &`

