# NEXT work unit (s1196)

HYPOTHESIS-ID: m4-vmadh-accumulator-origin

Work unit: perform one bounded independent oracle execution-mode/reachability
check for the M4 shaded phase. Run both oracle arms in this iteration: the
debugger-on arm retains a whole-RDRAM positive control and no target watch;
the debugger-off arm uses `--vi-poll` plus `--pif-trace` as independent phase
and input controls. Do not run the M4 target watch again until a matching
shaded VI phase is reached.

Competing hypotheses and discriminator:

- H1: debugger/watch instrumentation is causing the retail post-boot stall.
  If debugger-off `--vi-poll` advances beyond width 320 while debugger-on
  remains at width 320, the execution mode is the discriminator.
- H2: the input schedule is not reaching the intended state path. If both
  arms show the same PIF button reads and both remain at width 320, input is
  not the differing factor.
- H3: the retail ROM/core state path itself remains at width 320 under both
  modes. If both arms pass their controls, show the same eleven input events,
  and remain at width 320, select H3 and redesign the reachability route.

Positive controls: debugger-on whole-RDRAM watch must reach 10,000 callbacks;
debugger-off `--vi-poll` must report a nonzero width; `--pif-trace` must show
the scheduled Start reads. Phase comparisons use VI transitions, not elapsed
wall time.

Exact commands (run both arms, 180 seconds each):

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 180 --watch-write 0x0:0x800000 --vi-trace --pif-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start`

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 180 --oracle-debugger 0 --oracle-emulator 1 --vi-poll --pif-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start`

If H1 is selected, use the debugger-off phase transition as the next M4
reachability route. If H2 is selected, repair the input recipe before any
target watch. If H3 is selected, document the dual-mode controlled stall and
ask for a new retail execution path; do not infer ownership from a null.
