# NEXT work unit (s2414) — test whether the sequence key is legitimate

HYPOTHESIS-ID: m5-sequence-key-legitimacy

## Work unit

Run one bounded, observation-only reducer over the two valid image captures
(`s2412` and `s2413`). For every retained identity row, join the selected
first-later key-on event to the image stage event and report the complete
table by phase, stage event, key-on event, route ordinal/row, and event delta.
Do not change task data, audio, gate, fallback, dispatch, VI, output behavior,
the nonzero predicate, or the 64-event window.

## Competing hypotheses and discriminator

- H-SequenceLegitimate: the selected key-on event has a stable, causal
  relationship to the image stage/task sequence in both captures.
- H-RouteOrdinalAlias: the apparent sequence match is only a consequence of
  the route ordinal/row or a repeated frame pattern; event deltas vary when
  ordinal/row differs.
- H-GlobalEventCollision: the same global event stream collides with unrelated
  image rows; matching rows are not phase- or task-local.
- H-NoLegitimateRelation: the repeated class split does not survive the
  complete event-delta/route-local reducer.

The discriminator is one combined table, not a new field: counts and min/max
event deltas for class-5 and class-7 rows, partitioned by capture, phase,
route ordinal/row equality, and stage/task ordering. Stable nonzero deltas in
both captures with route-local ordering selects H-SequenceLegitimate; rows
whose deltas vary only with ordinal/row select H-RouteOrdinalAlias; matches
spanning unrelated phases or tasks select H-GlobalEventCollision; an empty or
unstable table selects H-NoLegitimateRelation. A missing input marker is
route-invalid.

## Exact commands

`python3 - <<'PY' scratch/agent/s2412_identity_join/image/run.log scratch/agent/s2413_identity_join/image/run.log`

The reducer must parse `[m5-identity-table]` lines, print the full bounded
summary, and write its output to `scratch/agent/s2414_sequence_legitimacy/`.
If no reducer exists, create it as a tracked script before running; do not
interpret raw run-log nulls without the positive-control and phase markers.

Required controls in each input: title `1024 @ 0x00790400`, hangar
`512 @ 0x006AB400`, and a key-on positive-control marker.
