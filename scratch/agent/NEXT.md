# Next: M4 accumulator boundary — new task/stage timing angle

Work unit: use the existing task-keyed retail capture and the qualified port
task-keyed capture to compare phase-5 transient-`0x8000` timing by port stage
(`10..13`) and task coverage. This is a bounded analysis; do not build or soak.

Competing hypotheses and discriminator:

- H1: the port's transient state is stage-equivalent to retail: `0x8000`
  appears in the pre-clear stage window and is absent at later stages/task end.
- H2: the port has a different lifetime/order: `0x8000` persists into later
  stages or task end, selecting an M4 implementation divergence.
- H3: stage hooks do not cover enough of the task to discriminate timing;
  report the comparison as unevaluable rather than infer equivalence.

Discriminating measurement: phase-5 rows must include the retail positive
controls and a task-keyed port table. Compare per-stage `0x8000` incidence,
the set of covered task IDs, and task-end `sat8000`; H1/H2 require matching
coverage and a pre-clear-only pattern, while H3 is selected by incomplete or
non-comparable coverage.

Inputs:
`scratch/agent/m4_task_join_run/{mid.dump,rsp.dump,oracle.log}`
`scratch/agent/m4_port_task_join_20261017f/port.log`

Session 5319 result: `markLowLodCellsInGrid = 0x80043AEC` was already
synchronized with zero edits. The preceding 15 titles were all sweep-scoped,
so this iteration was required to revisit a parked boundary instead of taking
the next symbol candidate.

HYPOTHESIS-ID: m4-accumulator-stage-timing
