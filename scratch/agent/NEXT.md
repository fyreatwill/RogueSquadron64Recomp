# NEXT work unit (s1198)

HYPOTHESIS-ID: m4-vmadh-accumulator-origin

Work unit: run one debugger-enabled retail input control with two arms: the
undriven baseline and a revised input schedule derived from s1197's observed
PIF words. Keep the whole-RDRAM watch and `--pif-trace` in both arms. The
revised schedule must test a single timing/state-path change, and comparison
is by PIF words and VI transitions/origins, not wall-clock timing. Do not arm
an M4 target watch until a later VI phase is reached.

Competing hypotheses and discriminator:

- H1: the revised timing is still wrong. If revised PIF words differ but VI
  remains at 320, the tested schedule change did not drive the intended path.
- H2: a distinct button phase or hold duration is required. If the revised arm
  reaches a later VI phase while its PIF words differ from baseline, the input
  path is sufficient and the prior schedule was incomplete.
- H3: retail remains at width 320 independently of input. If revised and
  undriven PIF/VI traces converge despite a materially different schedule, the
  blocker is a broader retail-state issue.

Positive controls: each arm's whole-RDRAM watch must reach 10,000 callbacks;
each arm must emit debugger-enabled PIF trace records. A null without both
controls is invalid.

Exact commands (run both arms in this iteration, 60 seconds each; the revised
arm adds the documented 150 ms hold duration):

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 60 --watch-write 0x0:0x800000 --vi-trace --pif-trace`

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 60 --watch-write 0x0:0x800000 --vi-trace --pif-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150`

If H1 is selected, make one further schedule change using the observed PIF
phase. If H2 is selected, retain the revised route and arm the next independent
reachability measurement. If H3 is selected, retain the input route and request
a new independent retail execution path; do not infer M4 ownership from a
null.
