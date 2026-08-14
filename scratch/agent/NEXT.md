# NEXT work unit (s1006)

The s1005 range/serial join ran successfully and selected
`H-child-range-only`; accepted ranges are child-DL-shaped and do not map an
individual F5 source update.

HYPOTHESIS-ID: m4-zero-shade-source-consumer-join

## One work unit

Add one bounded cross-layer trace that records the task-global F5 VTXCOLOR
ordinal/source immediately before each emitted RDP triangle command, alongside
the existing RT64 triangle consumer serial/range. Preserve existing shade rows.
Do not add a mitigation or hand-edit generated files.

Competing hypotheses and discriminating measurement:

- `H-triangle-source-join`: ordered F5 VTXCOLOR state and emitted triangle rows
  identify the source update feeding a zero-shade replacement.
- `H-child-range-only`: the consumer remains associated only with its child DL.
- `H-triangle-source-missing`: F5 state is not live at triangle emission or the
  stream has no usable ordered join.

The discriminating measurement is a same-run table keyed by task, F5 root DL,
F5 update ordinal/source, triangle emission order, submit serial/range, RT64
DL, and shade ordinal. The capture is invalid unless positive controls, root
identity, triangle rows, range-bearing shade rows, and zero-shade rows all fire
in the VI-1024-gated phase.

## Exact command

Build Debug, then launch:

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VTX_GENERATED_WRITES=1 ROGUESQ_LOG_VTX_WRITE_FAULT=1 ROGUESQ_LOG_F5_STATE=1 ROGUESQ_LOG_SHADE_RAW=1 ROGUESQ_LOG_TRI_WRITER=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a' zsh tools/probe.sh scratch/agent/s1006_triangle_source_join_20260814 180 3`

An individual F5 source immediately preceding a matching consumer triangle
selects `H-triangle-source-join`; only child-DL association selects
`H-child-range-only`; absent/unstable state selects
`H-triangle-source-missing`. If any positive control fails, record the run as
invalid and make no causal selection.
