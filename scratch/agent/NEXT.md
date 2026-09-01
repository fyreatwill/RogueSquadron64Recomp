# NEXT work unit — trace the upstream read/selector for extra task operands

HYPOTHESIS-ID: m5-task-field-writer

Session 3484 rejected the candidate-span store hypothesis: the port source-span
census saw initialization and nearby-field stores but no writes of the extra
operands. Session 3483 selected the writer-operand hypothesis: retail post-store values
at `0x8009177C/0x80091784` are restricted to `0x80171CE0`/`0x80173B20` and
sizes 1/2, while port writer and enqueue rows also carry
`0x8018FB70`/size 3 and `0x8018DD30`/size 1.

Competing hypotheses and discriminating outcomes:

- `H-SelectorDivergence`: the port reads a different table entry or selector
  before `0x8009177C/0x80091784`; a divergent read/selector row selects this.
- `H-GuestTransform`: the selected source value matches retail, then guest code
  transforms it before the writer; matching read rows plus differing writer
  rows selects this.
- `H-ObservationInvalid`: controls or the title phase fail; no conclusion is
  valid without both positive controls and title rows.

Discriminating measurement: one title-gated capture of the guest loads and
selector inputs immediately preceding the `0x8009177C/0x80091784` stores,
covering both extra and normal operands in the same rows. Retain the existing
whole-RDRAM and task-writer controls. A selector/read mismatch selects
`H-SelectorDivergence`; matching selected values followed by a writer mismatch
selects `H-GuestTransform`; absent controls make the result invalid.

Expected commands: first ask the independent Rice oracle for the selected
read/selector PCs or table span, then build only if a new regeneration-safe
port hook is needed. Run the port from `build/` with
`ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_SOLO=1`,
`ROGUESQ_LOG_M5_TASK_WRITER=1`, and the existing title phase controls. Use
SIGKILL watchdog cleanup and do not compare sequential animation ordinals.
