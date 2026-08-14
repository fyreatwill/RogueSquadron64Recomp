# NEXT work unit (s999)

HYPOTHESIS-ID: m4-zero-shade-source-consumer-join

## One work unit

Stamp the current F5 task serial on each `[f5-state-payload]` row, then join
the task/DL-identified zero-shade records to the same-task VTXCOLOR source
population and generated-store rows in one phase-gated capture. Do not add a
mitigation or hand-edit generated files.

Competing hypotheses and discriminating measurement:

- H-exact-zero-source: the zero-shade task's source population has only
  same-run generated writes.
- H-untouched-zero-source: it has nonzero payloads and no same-run generated
  writes.
- H-mixed: both source populations occur.

The discriminating measurement is the common task serial on payload and
shade-side rows, with display-list identity retained for each replacement. A
run with no controls, no stamped payload rows, no raw-shade records, or no
source rows is invalid.

## Exact commands

Add the task serial to the existing F5 payload diagnostic at its producer,
preserving source and payload bytes. Run the fixup static check, regenerate/build
in the documented order with `RS64_FIXUP_S992_GENERATED_WRITES=1`, then launch:

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VTX_GENERATED_WRITES=1 ROGUESQ_LOG_VTX_WRITE_FAULT=1 ROGUESQ_LOG_F5_STATE=1 ROGUESQ_LOG_SHADE_RAW=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a' zsh tools/probe.sh scratch/agent/s999_vtx_payload_task_join_20260813 180 3`

Extract phase-4/phase-6 payload, generated-write, raw-shade, and zero-shade
rows. Join by task serial and retain the DL identity when reporting each
replacement. Select a hypothesis only if all positive controls fire.
