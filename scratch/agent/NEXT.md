# NEXT work unit (s1004)

HYPOTHESIS-ID: m4-zero-shade-source-consumer-join

## One work unit

Add the accepted DPC submission range and submit serial to each RT64
task/DL-local shade row. Preserve the F5 root DL, F5 update ordinal/source,
and zero-shade replacement ordinal. Do not add a mitigation or hand-edit
generated files.

Competing hypotheses and discriminating measurement:

- H-submission-range-source-join: a shade row's RT64 submission interval and
  serial identify the F5 source update feeding it.
- H-child-range-only: the interval joins only the child DL and cannot identify
  an individual F5 source.
- H-range-coverage-incomplete: the RT64 row has no matching accepted interval.

The discriminating measurement is a same-run table keyed by task, F5 root DL,
F5 update ordinal/source, submit serial/range, RT64 DL, and RT64 ordinal. The
capture is invalid if controls, root identity, range-bearing shade rows, or
zero-shade rows do not all fire in the VI-1024-gated phase.

## Exact commands

Run the static fixup check, build Debug, then launch:

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VTX_GENERATED_WRITES=1 ROGUESQ_LOG_VTX_WRITE_FAULT=1 ROGUESQ_LOG_F5_STATE=1 ROGUESQ_LOG_SHADE_RAW=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a' zsh tools/probe.sh scratch/agent/s1004_submit_range_20260814 180 3`

Expected outcomes: a unique submit interval/serial consistently associated
with the zero-shade child DL selects H-submission-range-source-join; only
child-DL coverage selects H-child-range-only; missing rows select
H-range-coverage-incomplete. If any positive control fails, record the run as
invalid and make no causal selection.
