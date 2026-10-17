# Session 5298 M4 port task-keyed accumulator capture

The qualified port route was run with the task-keyed M4 probes, phase-gated
from phase 5. A documented cap value of `0` means immediate suppression in
the current implementation, so the corrected invocation used `1000000000`.
It emitted 826,080 mid-task rows and 3,744 task-end rows.

The VI-512 and probe controls fired. The reduction found 234 task IDs with
mid-task rows, 200 with a sampled `0x8000` lane, and 232 joined task-end rows.
The end stream contained 3,746 unique task IDs, so the mid-task hook covers
only a subset of phase-qualified graphics tasks. End-task `sat8000` was zero
in phases 5 and 7; the nonzero phase-3/6 rows are outside this M4 comparison
window.

This does not select H1 versus H2. H3 remains: the existing mid-task probe is
M4-stage selective and cannot produce a complete per-task table comparable to
the retail table. The port shows transient `0x8000` state, but no mitigation
or accumulator-origin conclusion follows.
