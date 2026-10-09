# Next work unit (s4395): independent direction split for published-word matches

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4394 qualified retail capture favored H-maintenance, but is single-source
evidence. The next unit is one bounded oracle instrument/run that splits the
existing snapshotted task-word comparison by writer-before-task versus
writer-after-task, retaining the same four exact fields, semantic/maintenance
classes, scalar checks, whole-RDRAM control, and three VI buckets.

Competing hypotheses:

- H-maintenance-stable: maintenance remains the stronger source/post match in
  both ordinal directions; this supplies an independent line for the bounded
  value result.
- H-directional: the match advantage exists only before or only after task
  publication; the nearest-task comparison is mixing distinct lifecycle edges.
- H-transform-gap: both classes remain mixed or absent after the direction
  split, so the transform/publication boundary remains open.

Discriminating measurement: for every joined scalar writer, compare the
snapshotted task word against the source lane and predicted post-store word,
keyed by phase, writer class, and ordinal relation (`before`, `after`, `equal`).
Controls are whole-RDRAM threshold >=10,000, title origins `0x00790400` and
`0x00790800`, hangar `0x006AB400`, valid type-2 rows >=1,000, ordinal overflow
0, and supported scalar mismatch 0. A missing control is invalid, not a null.

Exact commands:

    bash tools/oracle/build.sh
    bash scratch/agent/run_s4395_m5_published_word_direction.sh

The script must run one 75-second Rice/oracle capture from the repo root and
write its log below `scratch/agent/s4395_m5_published_word_direction/`.
