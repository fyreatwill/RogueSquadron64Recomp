# NEXT work unit (s1197)

HYPOTHESIS-ID: m4-vmadh-accumulator-origin

Work unit: run one debugger-enabled retail input control with two arms: an
undriven baseline and the eleven-Start schedule. Use the whole-RDRAM watch as
the positive control in both arms and `--pif-trace` to verify the actual button
words. Compare only VI transitions and origins, not wall-clock timing. Do not
arm an M4 target watch.

Competing hypotheses and discriminator:

- H1: the input injection/configuration is wrong. If driven and undriven arms
  have identical PIF button reads and identical VI transitions, input delivery
  is the discriminator.
- H2: input lands, but the eleven-Start schedule does not drive the intended
  state path. If driven PIF reads differ from undriven while VI remains at 320,
  the schedule/path is the remaining issue.
- H3: the retail execution path remains at width 320 independently of input.
  If driven PIF reads differ and driven reaches the same later VI phases as the
  documented control, the input route is validated and the remaining blocker
  is a retail-state reachability issue.

Positive controls: each arm's whole-RDRAM watch must reach 10,000 callbacks;
each arm must emit debugger-enabled PIF trace records. A null without both
controls is invalid.

Exact commands (run both arms in this iteration, 60 seconds each):

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 60 --watch-write 0x0:0x800000 --vi-trace --pif-trace`

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 60 --watch-write 0x0:0x800000 --vi-trace --pif-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start`

If H1 is selected, repair the input mapping before any M4 target watch. If H2
is selected, redesign the schedule using the observed PIF words and phase
transitions. If H3 is selected, retain the input route and request a new
independent retail execution path; do not infer M4 ownership from a null.
