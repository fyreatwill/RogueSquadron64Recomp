# NEXT work unit (s1016)

HYPOTHESIS-ID: m4-zero-shade-accumulator-origin

Perform one bounded static audit of the phase gate and input-to-transition
mapping before another M4 run. Read `tools/probe.sh` and grep the implementation
of `PROBE_PHASE_WIDTH`, `PROBE_PHASE_TIMEOUT`, `PROBE_KEYS`, `PROBE_LEAVE_OK`,
and the VI phase recorder. Trace whether the requested 512 gate means an exact
VI width, a transition after a key event, or a phase ordinal that the current
menu/attract path cannot reach. Do not build or run unless the audit finds a
concrete missing control that must be tested.

Competing hypotheses and discriminating measurement:

- `H-gate-exact-width`: the harness waits for an exact width that this path
  never emits; enumerate every observed/possible width and compare the gate
  predicate.
- `H-key-schedule-phase`: Start is delivered, but the scripted event is at the
  wrong game state or frame; map each key event to the state/VI transition
  recorded by the probe.
- `H-probe-contract-mismatch`: the environment variable or timeout is parsed
  differently from the documented contract; compare parser/default behavior
  with the command used in s1016.

The discriminator is a source-level truth table: for each gate predicate,
input event, and VI transition, state whether s1016's observed sequence can
 satisfy it. A single unambiguous mismatch selects one hypothesis and gives
 the exact corrected command for the next runtime capture. If all predicates
 are satisfiable but no 512 transition is game-reachable, report the missing
 state/input prerequisite rather than rerunning the accumulator probe.

Exact starting commands:

`rg -n 'PROBE_PHASE_WIDTH|PROBE_PHASE_TIMEOUT|PROBE_KEYS|PROBE_LEAVE_OK|512|phase' tools/probe.sh tools src lib | head -240`

`rg -n 'PROBE_PHASE_WIDTH|PROBE_PHASE_TIMEOUT|PROBE_KEYS|PROBE_LEAVE_OK|vi_width|phase' src lib tools -g '*.{c,cpp,h,sh,ps1}'`
