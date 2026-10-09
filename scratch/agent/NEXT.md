# Next work unit (s4392): classify exact-span writer PC/value classes by task ordinal

HYPOTHESIS-ID: m5-selector-decode-boundary

Competing hypotheses:

- H-semantic-pc-class: `0x80090DE4`/`0x80090B68` are the semantic exact-span
  writers and remain inside the corresponding task publication lifecycle.
- H-maintenance-pc-class: `0x80090CA4`/`0x80091078` account for the target-span
  traffic as setup/maintenance, while semantic stores are elsewhere.
- H-source-gap: the current ordinal and source-value fields cannot classify
  writer PCs without a new bounded lifecycle key.

Discriminating measurement: one retail-oracle run retaining all exact writer
rows for the four target watches, task event ordinals, source values, and a
phase-keyed writer-PC/value-class × task-lifecycle table. A consistent
semantic-PC class inside the corresponding task interval selects
H-semantic-pc-class; a distinct maintenance-PC class with semantic candidates
outside the interval selects H-maintenance-pc-class; missing-task, overflow,
or an unresolved class split selects H-source-gap.

Controls: whole-RDRAM positive control, title origins `0x00790400:1024` and
`0x00790800:1024`, hangar origin `0x006AB400:512`, at least 1,000 valid type-2
rows, zero task/ordinal overflow, and mismatch 0 for supported scalar stores.

Exact commands:

    inspect the s4391 runner and add the bounded PC/value-class table if it is
    not already retained
    bash scratch/agent/run_s4392_m5_exact_span_class.sh

Summarize only bounded `rg`/`sed` windows from the oracle log. Keep s4389/s4390
as qualified single-source destination evidence; do not repeat the union watch.
