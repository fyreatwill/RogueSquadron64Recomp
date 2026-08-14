# NEXT work unit (s956)

Validate the retail-oracle input/phase path before retrying the callback-table
watch. Do not build, edit generated code, add a guard, or interpret the table's
zero-hit result until the same run crosses VI width 320.

HYPOTHESIS-ID: m3-slotdispatcheriter-stacksp-class

The callback-table oracle arm is currently phase-unevaluable. The whole-RDRAM
watch passed, but the retail run stayed at VI 320; PIF tracing showed injected
state changes without establishing the documented Start transition.

Competing hypotheses:

- H-oracle-config-mapping: the active input configuration maps the injected
  values differently from the documented Start mapping.
- H-oracle-core-phase: input is accepted, but this core/ROM/config combination
  is stuck in an early retail phase for an unrelated setup reason.
- H-oracle-undriven-timeline: the run is healthy and simply needs the full
  undriven boot interval before the VI transition; the prior 45-second run was
  too short for this environment.
- H-oracle-callback-unclassified: the phase is reached, but the callback table
  remains unwritten or its writer/value path is not observable by this watch.

Discriminating measurement: run one oracle capture with the documented
`rs64-oracle/cfg` config, whole-RDRAM write positive control, PIF trace, VI
trace, and both a named `start` schedule and a no-input control arm built into
the same capture if the tool supports it. A PIF word corresponding to Start
plus VI > 320 selects config/input acceptance; whole-RDRAM hits with VI 320
selects an early-phase/setup issue; VI > 320 with zero callback-table writes
selects callback-unclassified. Do not use a table null from VI 320.

Exact starting commands:

`sed -n '1,220p' tools/oracle/README.md`

`tools/oracle/build/rs64_oracle --configdir /Users/williambuckley/Documents/Tools/rs64-oracle/cfg --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 90 --watch-write 0x0:0x800000 --watch-write 0x10B350:0x10B750 --hit-cap 200 --detail-watch 1 --vi-trace --pif-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 > scratch/agent/oracle_results/s956_callback_phase/run.log 2>&1`

The whole-RDRAM watch must visibly fire. Report VI width transitions and PIF
words first; only then classify the callback-table watch.
