# M5 Session 3663 — writer caller and all-phase census

The retail oracle field dump now includes `prev_pc` and `$ra`, plus an
explicit all-VI-phase mode. Controls were valid: 133,677 whole-RDRAM writes,
1,107 valid type-2 task rows, zero invalid task pointers, 632 title VIs, and
481 hangar VIs. The dominant `0x80090DE4` family retained
`prev_pc=0x80090DE0` and `$ra=0x80090ABC` across target and non-target 512
phase buckets, ruling out a caller-family split.

Logical ownership remains unresolved. This run's task rows were
`data_ptr=0x80173B20` in title and `0x80173CB0` in hangar, unlike s3662's
validated hangar `0x80171E70` tuple. The same low-level caller family is
present, but the route-dependent task-object difference must be explained
before selecting an all-phase producer or pre-phase initializer hypothesis.

The paired port arm crashed before phase controls, so it is invalid for this
census. Existing s3662 port controls remain the independent port-side line;
the new caller result is single-source retail evidence.

ORIGIN: diagnostic-only oracle fields and phase/task observations; no guest or
host value was skipped, rewritten, or guarded.
