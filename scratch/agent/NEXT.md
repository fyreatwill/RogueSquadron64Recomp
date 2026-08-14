# NEXT work unit (s1003)

HYPOTHESIS-ID: m4-zero-shade-source-consumer-join

## One work unit

Add a task-scoped snapshot of the F5-emitted DPC/RDP output range and print its
first/last physical range on the task's payload summary. Preserve the existing
root DL, F5 ordinal, and RT64 task/DL-local ordinal. Do not add a mitigation or
hand-edit generated files.

Competing hypotheses and discriminating measurement:

- H-dpc-range-contains-consumer: the emitted range contains the RT64 consumer
  DL.
- H-dpc-range-disjoint: the consumer comes from another task/range.
- H-no-range-join: range coverage is incomplete.

The discriminating measurement is a same-run table keyed by task, F5 root DL,
F5 update ordinal, F5 command address/source, DPC range, RT64 DL, and RT64
ordinal. A capture is invalid if the controls, root/range identity,
ordinal-bearing payloads, or zero-shade rows do not all fire in the gated
phase. Ground-truth status:
the retail oracle is independently available only for physical CPU-memory
writes and cannot observe this F5/RT64 stream; the F5 command semantics are
anchored by docs/F5-UCODE-REFERENCE.md, so this iteration measures joins and
makes no retail ownership claim.

## Exact commands

Thread each committed F5 DPC range into task-scoped provenance, print the
bounded first/last range once per task, run the static fixup check, export
submodule patches if needed, build Debug, then launch:

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VTX_GENERATED_WRITES=1 ROGUESQ_LOG_VTX_WRITE_FAULT=1 ROGUESQ_LOG_F5_STATE=1 ROGUESQ_LOG_SHADE_RAW=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a' zsh tools/probe.sh scratch/agent/s1000_vtx_source_consumer_20260813 180 3`

Join only phase-4/phase-6 rows after the VI-1024 gate. Report the F5 root DL,
source, generated-store overlap/value, DPC range, task, and ordinal against
every zero-shade replacement. Select one hypothesis only if all positive
controls and root/range identity coverage fire; otherwise record the run as
invalid and do not select a causal hypothesis.
