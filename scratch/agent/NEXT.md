# NEXT work unit (s1202)

HYPOTHESIS-ID: m4-vmadh-accumulator-origin

Work unit: run one debugger-enabled retail input control with two arms: the
undriven baseline and a schedule whose first Start is moved to `0.1s`, earlier
than the s1201 `0.2:start` press, retaining the 150 ms hold and later presses. Keep the
whole-RDRAM watch and `--pif-trace` in both arms. Compare by PIF words and VI
transitions/origins, not wall-clock timing. Do not arm an M4 target watch until
a later VI phase is reached.

Competing hypotheses and discriminator:

- H1: the `0.1:start` press changes PIF words but VI remains at 320; the
  tested schedule is still not driving the intended path.
- H2: the `0.1:start` press reaches a later VI phase while PIF words differ;
  the prior schedule's phase was incomplete.
- H3: revised and undriven PIF/VI traces converge despite the changed schedule;
  the blocker is broader than this input timing path.

Positive controls: each arm's whole-RDRAM watch must reach 10,000 callbacks;
each arm must emit debugger-enabled PIF trace records. A null without both
controls is invalid.

Exact commands (run both arms in this iteration, 60 seconds each):

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 60 --watch-write 0x0:0x800000 --vi-trace --pif-trace`

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 60 --watch-write 0x0:0x800000 --vi-trace --pif-trace --press 0.1:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150`

If H1 is selected, retain the route only as context and make the one
phase-informed schedule change above. If H2 is selected, retain the revised
route and arm the next independent reachability measurement. If H3 is
selected, retain the input route and request a new independent retail
execution path; do not infer M4 ownership from a null.
