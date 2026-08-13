# NEXT work unit (oracle runtime behavior check)

HYPOTHESIS-ID: oracle-runtime-identity-divergence

s775 found byte-identical oracle/core/RSP/input/ROM artifacts and configs that
differ only by `EnableDebugger`; the remaining question is runtime behavior,
not artifact identity.

## Competing hypotheses

- H-oracle-debugger-late-interference: `EnableDebugger` changes execution only
  after the shared initial 320 phase.
- H-oracle-schedule-or-timing: the documented later phase depends on a runtime
  scheduling/timing condition absent from this headless recipe.
- H-oracle-expected-320: the documented later phase is not reachable with this
  exact retail/core/plugin recipe, despite the positive controls.

## Discriminating measurement

Run one fresh matched debugger-on/off oracle A/B using the already verified
artifacts and the existing 70-second Start schedule. Keep the debugger-on
whole-RDRAM positive control and PIF trace; keep debugger-off raw VI polling.
Phase-gate the comparison on width/origin transitions. A later transition in
only one arm selects debugger interference; identical 320-only traces select
schedule/timing or expected-320 runtime behavior and rule out the debugger as
the late-phase cause.

## Commands

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 70 --oracle-debugger 1 --watch-write 0x0:0x800000 --vi-trace --pif-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 70 --oracle-debugger 0 --vi-poll --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150

Expected: both arms reach only width 320/origin `0x6dd280`, selecting
H-oracle-schedule-or-timing or H-oracle-expected-320; a later transition in
only one arm selects H-oracle-debugger-late-interference. The positive control
must fire in the debugger-on arm or the result is unevaluable.
