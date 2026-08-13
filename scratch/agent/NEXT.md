# NEXT work unit (s877)

HYPOTHESIS-ID: m3-coalesce-value-legitimacy

Run one paired, phase-gated value comparison for the four coalescer globals,
using the existing s875 regeneration-replayable origin probe on the port and
the retail oracle's physical write watches. Do not add a guard or change game
behavior. Verify positive controls and phase reach before interpreting null.

Competing hypotheses:

- H-port-value-matches-retail: writer values and transitions agree.
- H-port-value-diverges: a matched late writer differs.
- H-late-phase-unreachable: controls pass but the late tuple is not reached.

Discriminating measurement: the same writer/phase/value tuple on both sides.
Matching late tuples select H-port-value-matches-retail; a divergent matched
tuple selects H-port-value-diverges; absent tuples are valid only with phase
proof and positive controls, selecting H-late-phase-unreachable.

Exact commands: use the existing s875 probe/recipe and oracle instructions;
run the port from `build/`, capture to a non-hidden final path, and use
SIGKILL. Do not start a second build or an A/B stopwatch comparison.
