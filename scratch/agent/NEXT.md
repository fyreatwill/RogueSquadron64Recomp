# NEXT work unit — trace the upstream table entry writer for extra operands

HYPOTHESIS-ID: m5-task-field-writer

Session 3484 rejected the candidate-span store hypothesis: the port source-span
census saw initialization and nearby-field stores but no writes of the extra
operands. Session 3483 selected the writer-operand hypothesis: retail post-store values
at `0x8009177C/0x80091784` are restricted to `0x80171CE0`/`0x80173B20` and
sizes 1/2, while port writer and enqueue rows also carry
`0x8018FB70`/size 3 and `0x8018DD30`/size 1.

Session 3485 selected `H-SelectorDivergence`: the port's pre-writer chain
selected `0x8018FB70` and `0x8018DD30` at `0x800916F0`, while retail's paired
writer evidence remains restricted to `0x80171CE0`/`0x80173B20`. Both oracle
and port controls fired. The next unit must locate the upstream table entry
writer or pointer that feeds those extra port selections.

Competing hypotheses and discriminating outcomes:

- `H-EntryWriterDivergence`: the port writes or loads a different table entry
  or pointer before the selector; matching the extra value to a port-only
  writer selects this.
- `H-SharedEntryTransform`: both arms read the same entry, but guest code
  transforms it before `0x800916F0`; matching entry rows plus differing
  selected values selects this.
- `H-ObservationInvalid`: controls or the title phase fail; no conclusion is
  valid without both positive controls and title rows.

Discriminating measurement: one title-gated oracle-and-port capture of the
candidate table-entry span and its pointer/load sites, joined to the selected
`a0/a2` rows. A port-only entry writer or pointer selects
`H-EntryWriterDivergence`; identical entry values followed by different
selected operands selects `H-SharedEntryTransform`; absent controls make the
result invalid. Ask ground truth for the exact retail writer/read PCs before
building a new port hook.

Expected commands: first run the independent Rice oracle with whole-RDRAM and
candidate-entry controls plus execution watches; only then add a
regeneration-safe port hook if required. Run the port from `build/` with
`ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_SOLO=1`,
`ROGUESQ_LOG_M5_TASK_WRITER=1`, and the existing title phase controls. Use
SIGKILL watchdog cleanup and do not compare sequential animation ordinals.
