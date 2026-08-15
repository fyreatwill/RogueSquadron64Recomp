# NEXT work unit (s1205)

HYPOTHESIS-ID: retail-execution-mode-reachability

Work unit: run one debugger-enabled retail execution-mode comparison with two
arms: an undriven baseline and the documented hangar schedule with Start
presses at `6,11,16,21,26,31,36,41,46,51,56s`, both using
`--oracle-emulator 1` and 150 ms holds. Keep the whole-RDRAM watch,
`--pif-trace`, and `--vi-trace` in both arms. Compare by PIF words and VI
transitions/origins, not wall-clock timing. Do not arm an M4 target watch until
a later VI phase is reached.

Competing hypotheses and discriminator:

- H1: alternate emulator mode still changes driven PIF words but both arms
  remain at VI 320; route failure is independent of interpreter mode.
- H2: alternate emulator mode reaches a later VI phase in the driven arm;
  interpreter execution was the reachability blocker.
- H3: either arm fails its whole-RDRAM/PIF controls; the comparison is invalid
  and the execution-mode explanation is not tested.

Positive controls: each arm's whole-RDRAM watch must reach 10,000 callbacks;
each arm must emit debugger-enabled PIF and VI trace records. A null without
both controls is invalid.

Exact commands (run both arms in this iteration, 60 seconds each):

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 60 --watch-write 0x0:0x800000 --vi-trace --pif-trace --oracle-emulator 1`

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 60 --watch-write 0x0:0x800000 --vi-trace --pif-trace --oracle-emulator 1 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150`

If H1 is selected, retain the mode-independent failure and seek a different
retail execution path. If H2 is selected, retain the alternate mode and arm
the next independent reachability measurement. If H3 is selected, repair the
control setup before drawing any conclusion.
