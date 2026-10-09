# Next work unit (s4390): classify exact-span writers

HYPOTHESIS-ID: m5-selector-decode-boundary

Competing hypotheses:

- H-semantic-data: the exact task-span stores carry the semantic payload.
- H-maintenance-data: the exact task-span stores are maintenance/zero-fill;
  semantic values are written elsewhere.
- H-source-gap: post-store scalar attribution or the phase/ordinal join is not
  sufficient to classify the exact-span writers.

Discriminating measurement: one retail-oracle run with exact watches for both
observed hangar data spans and their exact `+0x100` fields, plus
`--post-value-watch` and post-store scalar validation for every target watch.
Valid nonzero scalar writes from the publication-linked writer PCs select
H-semantic-data; only zero-fill/maintenance writes with a live writer outside
those spans select H-maintenance-data; mismatch, unsupported, missing-task, or
overflow rows select H-source-gap.

Controls required: whole-RDRAM positive control, title origins
`0x00790400:1024` and `0x00790800:1024`, hangar origin `0x006AB400:512`, at
least 1,000 valid type-2 rows, zero target-watch and ordinal overflow, and
phase-scoped scalar mismatch/unsupported counts of zero.

Exact commands:

    bash tools/oracle/build.sh
    edit scratch/agent/run_s4390_m5_exact_span_scalar.sh from the s4389 runner,
    adding post-value/post-store-scalar arms for watches 1-5
    bash scratch/agent/run_s4390_m5_exact_span_scalar.sh

Summarize only bounded `rg`/`sed` windows from the oracle log. Keep the s4389
result as qualified single-source destination evidence; do not repeat the
union watch.
