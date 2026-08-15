# NEXT work unit (s1204)

HYPOTHESIS-ID: m4-vmadh-accumulator-origin

Work unit: run one debugger-enabled retail input control with two arms: the
undriven baseline and the documented hangar schedule with Start presses at
`6,11,16,21,26,31,36,41,46,51,56s`, retaining the 150 ms hold. Keep the
whole-RDRAM watch and `--pif-trace` in both arms. Compare by PIF words and VI
transitions/origins, not wall-clock timing. Do not arm an M4 target watch until
a later VI phase is reached.

Competing hypotheses and discriminator:

- H1: the documented schedule changes PIF words but VI remains at 320; the
  apparent hangar route is not reproducible in this oracle configuration.
- H2: it reaches a later VI phase while PIF words differ; the prior schedules
  were phase-incomplete and the documented route is valid.
- H3: driven and undriven PIF/VI traces converge despite the documented
  schedule; the blocker is broader than this input timing path.

Positive controls: each arm's whole-RDRAM watch must reach 10,000 callbacks;
each arm must emit debugger-enabled PIF trace records. A null without both
controls is invalid.

Exact commands (run both arms in this iteration, 60 seconds each):

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 60 --watch-write 0x0:0x800000 --vi-trace --pif-trace`

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 60 --watch-write 0x0:0x800000 --vi-trace --pif-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150`

If H1 is selected, retain the documented-route failure as context and seek a
new independent retail execution path. If H2 is selected, retain the revised
route and arm the next independent reachability measurement. If H3 is
selected, retain the input route and request a new independent retail
execution path; do not infer M4 ownership from a null.
