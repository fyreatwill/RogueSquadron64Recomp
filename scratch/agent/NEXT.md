# NEXT work unit (s1210)

HYPOTHESIS-ID: retail-execution-path-reachability

Work unit: run one debugger-enabled retail reachability comparison in the
remaining R4300 emulator mode, paired with an undriven control. Mode 1 was
already phase-incomplete; test whether mode 2 changes execution ordering or
state progression. Driven presses are the documented cadence
`6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start`.
Preserve the whole-RDRAM watch, `--pif-trace`, and `--vi-trace` in both arms.
Do not arm an M4 target watch until a later VI phase is reached.

Competing hypotheses and discriminator:

- H1: emulator mode 2 changes the retail state path and the driven arm reaches
  a later VI phase/origin than width 320 / `0x006dd280`.
- H2: both arms remain at VI 320 / `0x006dd280` while controls pass; emulator
  execution mode is not the missing retail entry mechanism.
- H3: either arm fails whole-RDRAM or PIF/VI controls; the comparison is
  invalid and the mode hypothesis is untested.

Positive controls: each arm's whole-RDRAM watch must reach 10,000 callbacks;
the driven arm must show all eleven PIF-confirmed Start press/release pairs;
both arms must emit debugger-enabled VI records. A null without all controls
is invalid.

Exact commands (run from the repository root, 60 seconds each):

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom build/rogue_squadron.z64 --secs 60 --oracle-emulator 2 --watch-write 0x0:0x800000 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 --vi-trace --pif-trace > scratch/agent/oracle_mode2_driven.log 2>&1
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom build/rogue_squadron.z64 --secs 60 --oracle-emulator 2 --watch-write 0x0:0x800000 --vi-trace --pif-trace > scratch/agent/oracle_mode2_undriven.log 2>&1

If H1 is selected, retain the path change and arm the resulting later-phase
measurement. If H2 is selected, seek a different retail execution path. If
H3 is selected, repair the control setup before drawing a conclusion.
