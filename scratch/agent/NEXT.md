# NEXT work unit (s1211)

HYPOTHESIS-ID: retail-entry-strategy

Work unit: run one debugger-enabled retail reachability comparison using a
controller-chord sweep before the documented Start cadence, paired with an
undriven control. This is a new input path, not another title-time A timing
variation. Run both arms concurrently with the whole-RDRAM watch,
`--pif-trace`, and `--vi-trace`; do not arm an M4 target watch until a later VI
phase is reached.

Competing hypotheses and discriminator:

- H1: the new entry mechanism changes the retail state path and the driven arm
  reaches a later VI phase/origin than width 320 / `0x006dd280`.
- H2: both arms remain at VI 320 / `0x006dd280` while controls pass; the new
  input mechanism is not sufficient to enter the later path.
- H3: either arm fails whole-RDRAM or PIF/VI controls; the comparison is
  invalid and the entry hypothesis is untested.

Positive controls: each arm's whole-RDRAM watch must reach 10,000 callbacks;
the driven arm must show the new input event in PIF reads; both arms must emit
debugger-enabled VI records. A null without all controls is invalid.

Exact commands (run from the repository root, 60 seconds each):

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom build/rogue_squadron.z64 --secs 60 --watch-write 0x0:0x800000 --press 0.5:a,1.0:b,1.5:z,2.0:l,2.5:r,3.0:up,3.5:down,4.0:left,4.5:right,6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 --vi-trace --pif-trace > scratch/agent/oracle_chord_driven.log 2>&1
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom build/rogue_squadron.z64 --secs 60 --watch-write 0x0:0x800000 --vi-trace --pif-trace > scratch/agent/oracle_chord_undriven.log 2>&1

If H1 is selected, retain the path change and arm the resulting later-phase
measurement. If H2 is selected, seek another independent entry strategy. If
H3 is selected, repair the control setup before drawing a conclusion.
