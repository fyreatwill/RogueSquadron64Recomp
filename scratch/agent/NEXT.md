# NEXT work unit (oracle execution-backend check)

HYPOTHESIS-ID: oracle-runtime-identity-divergence

s777 repeated the matched debugger-on/off check. The debugger-on positive
control fired 11,768,621 whole-RDRAM writes over 4,193 VI and logged all 11
presses. Debugger-off raw polling stayed at width 320/origin `0x6dd280` for 70
seconds and returned the documented clean zero-hit rc=3. The remaining question
is whether the R4300 execution backend changes the retail phase timeline.

## Competing hypotheses

- H-oracle-schedule-or-timing: the documented later phase depends on a runtime
  scheduling/timing condition absent from this headless recipe.
- H-oracle-expected-320: the documented later phase is not reachable with this
  exact retail/core/plugin recipe, despite the positive controls.
- H-oracle-emulator-backend: the alternate R4300 execution backend changes
  scheduling or execution enough to reveal the later phase.

## Discriminating measurement

Run both fresh 70-second arms concurrently with the verified artifacts and
`--oracle-emulator 1`, retaining the debugger-on whole-RDRAM positive control,
PIF trace, and debugger-off raw VI polling. Phase-gate on width/origin
transitions. A later transition in either arm selects the emulator-backend
hypothesis; identical 320-only traces rule out that backend as the missing
phase and leave schedule/timing versus expected-320 behavior.

## Commands

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 70 --oracle-debugger 1 --oracle-emulator 1 --watch-write 0x0:0x800000 --vi-trace --pif-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 70 --oracle-debugger 0 --oracle-emulator 1 --vi-poll --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150

Expected: both arms remain at width 320/origin `0x6dd280`, with a positive
whole-RDRAM control in the debugger-on arm; this rules out the alternate
execution backend as the missing phase. A later transition in either arm
selects H-oracle-emulator-backend.
