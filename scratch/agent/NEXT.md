# NEXT work unit (s958)

Audit the oracle's actual config/input-plugin path, then run a bounded
30-second undriven versus named-`start` phase control without `--configdir`.
The s957 run proved the watch and press scheduler, but contradicted the
documented phase timeline; callback-table nulls remain uninterpretable. No
build or generated-code edit is needed.

HYPOTHESIS-ID: m3-slotdispatcheriter-stacksp-class

Competing hypotheses:

- H-oracle-config-path: `--configdir` is ignored or the selected input plugin
  is using a different mapping/config than the documented setup.
- H-oracle-core-phase: the configured core/RSP/setup genuinely remains at VI
  320 despite accepted button injections.
- H-oracle-timeline: the exact recipe progresses only after a longer emulated
  interval, so 30 seconds is insufficient.

Discriminating measurement: inspect command/config wiring, then compare paired
30-second runs using named `start`, a whole-RDRAM positive control,
`--vi-poll`, and `--pif-trace`. An actual config-path/input-map discrepancy
selects config-path; VI >320 in the corrected arm selects stale-config; both
arms at VI 320 with the documented plugin path selects core/setup; a late
transition only in the longer control selects timeline. The positive control
must visibly fire in both arms.

Exact starting commands (create the result directory first):

`mkdir -p scratch/agent/oracle_results/s958_oracle_phase`

`rg -n "Input-SDL-Control1|Start|plugin" /Users/williambuckley/Documents/Tools/rs64-oracle/cfg`

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 30 --watch-write 0x0:0x800000 --hit-cap 200 --vi-poll --pif-trace > scratch/agent/oracle_results/s958_oracle_phase/undriven.log 2>&1`

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 30 --watch-write 0x0:0x800000 --hit-cap 200 --vi-poll --pif-trace --press 6:start,11:start,16:start,21:start,26:start > scratch/agent/oracle_results/s958_oracle_phase/driven.log 2>&1`
