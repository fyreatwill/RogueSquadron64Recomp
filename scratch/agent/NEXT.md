# NEXT work unit (s1000)

HYPOTHESIS-ID: m4-zero-shade-source-consumer-join

## One work unit

Add a phase-scoped ordinal to each F5 `0x02` VTXCOLOR payload update and to
each RT64 raw-shade/zero-shade record for the same task/DL stream. Use the
ordinal and display-list identity to test whether zero-shade replacements
follow one identifiable source update, rather than merely sharing task 204
with a mixed source population. Do not add a mitigation or hand-edit
generated files.

Competing hypotheses and discriminating measurement:

- H-source-ordinal: every zero-shade DL maps to one preceding/current F5
  source ordinal, and those mapped sources have a consistent ownership class.
- H-dl-boundary: the mapping resets or changes at the DL boundary; source
  identity is determined by DL-local order, not task-global order.
- H-no-consumer-join: no stable ordinal/DL mapping exists, so the task-level
  mixed result cannot identify the consumer source.

The discriminating measurement is a same-run table keyed by task, F5 update
ordinal, RT64 command/DL identity, and source address. A capture is invalid if
the F5 fetch/state controls, raw-shade control, zero-shade rows, or source
rows do not all fire in the gated phase.

## Exact commands

Implement the ordinal fields in the existing `rs64_f5_state_probe` payload
diagnostic and the RT64 `[shade-raw]`/`[fix-zero-shade]` diagnostics, preserving
the existing task, source, payload, and DL fields. Run the static fixup check,
regenerate/build in the documented order with
`RS64_FIXUP_S992_GENERATED_WRITES=1`, then launch:

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VTX_GENERATED_WRITES=1 ROGUESQ_LOG_VTX_WRITE_FAULT=1 ROGUESQ_LOG_F5_STATE=1 ROGUESQ_LOG_SHADE_RAW=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a' zsh tools/probe.sh scratch/agent/s1000_vtx_source_consumer_20260813 180 3`

Join only phase-4/phase-6 rows after the VI-1024 gate. Report the mapped
source address, generated-store overlap/value, task, and DL for every
zero-shade replacement. Select H-source-ordinal, H-dl-boundary, or
H-no-consumer-join only if all positive controls fire and the mapping outcome
is reproducible within the single capture.
