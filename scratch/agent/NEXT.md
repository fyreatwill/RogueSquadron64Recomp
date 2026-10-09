# Next work unit (s4391): map semantic exact-span writers to task ordinals

HYPOTHESIS-ID: m5-selector-decode-boundary

Competing hypotheses:

- H-ordinal-semantic: validated nonzero exact-span stores occur in the task
  publication interval and are semantic payload.
- H-ordinal-maintenance: the nonzero stores are setup/maintenance traffic and
  do not align with individual task publications.
- H-source-gap: the current exact-span scalar/ordinal keys cannot separate the
  two classes without a new bounded field.

Discriminating measurement: one retail-oracle run retaining exact writer rows
for the four target watches, task event ordinals, source values, and phase-keyed
nearest-task joins. A bounded table showing the same writer PC/value class
inside the publication interval selects H-ordinal-semantic; only rows outside
that interval with zero/maintenance signatures select H-ordinal-maintenance;
missing-task, overflow, or inability to retain the writer/value key selects
H-source-gap.

Controls: whole-RDRAM positive control, title origins `0x00790400:1024` and
`0x00790800:1024`, hangar origin `0x006AB400:512`, at least 1,000 valid type-2
rows, zero task/ordinal overflow, and mismatch 0 for supported scalar stores.

Exact commands:

    inspect the s4390 runner and extend the oracle's existing ordinal summary
    only if the writer/value-to-task table is not already retained
    bash scratch/agent/run_s4391_m5_exact_span_ordinal.sh

Summarize only bounded `rg`/`sed` windows from the oracle log. Keep s4389/s4390
as qualified single-source destination evidence; do not repeat the union watch.
