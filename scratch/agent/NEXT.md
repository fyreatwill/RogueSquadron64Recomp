# NEXT work unit (audit debugger-off oracle phase observation)

HYPOTHESIS-ID: oracle-320-only-divergence

s773 completed the long A/B: debugger-on had a positive control and 4,192 VI;
debugger-off logged all inputs and the same initial poll transition but cannot
provide a callback VI total or a later transition record. The next unit is one
bounded oracle-side observation audit, followed by one matched phase check if
the audit is a buildable change.

## Competing hypotheses

- H-oracle-poll-bug: `--vi-poll` is not sampling the effective VI registers
  after initialization; raw register logging will remain frozen or absent.
- H-oracle-real-320-only: raw debugger-off polling will show continuous
  width/origin samples with no later transition, matching debugger-on.
- H-oracle-debugger-interference: a trustworthy raw poll will show a later
  transition that differs from debugger-on, selecting debugger overhead or
  callbacks as causal.

## Discriminating measurement

First inspect the existing `--vi-poll` implementation and add one bounded,
phase-scoped raw-read diagnostic that emits the sampled VI width and origin at
fixed poll intervals without using debugger callbacks. Build the oracle, then
run matched fresh-config 70-second arms with the same schedule: debugger-on
with `--oracle-debugger 1 --vi-trace --pif-trace --watch-write 0x0:0x800000`,
debugger-off with `--oracle-debugger 0 --vi-poll`, and the same positive-control
requirements. A continuously changing raw poll proves the off-arm observation
path; frozen/absent raw samples select H-oracle-poll-bug; a trustworthy later
transition differing between arms selects H-oracle-debugger-interference; no
later transition in either arm selects H-oracle-real-320-only.

## Commands

   rm -rf /tmp/rs64-oracle-config-s773-a /tmp/rs64-oracle-config-s773-b scratch/agent/oracle-config-s773 && mkdir -p /tmp/rs64-oracle-config-s773-a /tmp/rs64-oracle-config-s773-b scratch/agent/oracle-config-s773
   tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --configdir /tmp/rs64-oracle-config-s773-a --secs 70 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --oracle-debugger 1 --vi-trace --pif-trace --watch-write 0x0:0x800000 > scratch/agent/oracle-config-s773/a.log 2>&1 & p1=$!
   tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --configdir /tmp/rs64-oracle-config-s773-b --secs 70 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --oracle-debugger 0 --vi-poll > scratch/agent/oracle-config-s773/b.log 2>&1 & p2=$!
   wait "$p1"; r1=$?; wait "$p2"; r2=$?; printf 'a_rc=%s b_rc=%s\n' "$r1" "$r2"
