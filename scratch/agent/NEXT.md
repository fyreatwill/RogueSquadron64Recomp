# NEXT work unit (s1001)

HYPOTHESIS-ID: m4-zero-shade-source-consumer-join

## One work unit

Add the F5 task's root display-list start address to shared task provenance and
print it on every `[f5-state-payload]` row. Preserve the existing task-global
F5 ordinal and RT64 task/DL-local ordinal. Normalize the root to the same
physical 23-bit address domain as the existing source/DL fields. Do not add a
mitigation or hand-edit generated files.

Competing hypotheses and discriminating measurement:

- H-root-dl-join: the F5 root DL identity matches one RT64 DL and its local
  ordinal.
- H-child-dl-join: the source is associated with a child DL that must be
  captured separately.
- H-no-consumer-join: root identity still cannot connect the streams.

The discriminating measurement is a same-run table keyed by task, F5 root DL,
F5 update ordinal, F5 command address/source, RT64 DL, and RT64 ordinal. A
capture is invalid if the controls, root identity, ordinal-bearing payloads,
or zero-shade rows do not all fire in the gated phase. Ground-truth status:
the retail oracle is independently available only for physical CPU-memory
writes and cannot observe this F5/RT64 stream; the F5 command semantics are
anchored by docs/F5-UCODE-REFERENCE.md, so this iteration measures joins and
makes no retail ownership claim.

## Exact commands

Thread `dl_ptr` from the graphics-task submitter into
`rs64_e9prov_task_begin` or an equivalent task-scoped provenance setter, print
it on the F5 payload rows, run the static fixup check, export submodule patches
if needed, build Debug, then launch:

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VTX_GENERATED_WRITES=1 ROGUESQ_LOG_VTX_WRITE_FAULT=1 ROGUESQ_LOG_F5_STATE=1 ROGUESQ_LOG_SHADE_RAW=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a' zsh tools/probe.sh scratch/agent/s1000_vtx_source_consumer_20260813 180 3`

Join only phase-4/phase-6 rows after the VI-1024 gate. Report the F5 root DL,
source, generated-store overlap/value, task, and ordinal against every
zero-shade replacement. Select one hypothesis only if all positive controls and
root identity coverage fire.
