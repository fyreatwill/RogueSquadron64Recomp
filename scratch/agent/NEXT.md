# NEXT work unit (s1007)

s1006 reached VI 1024, passed all controls, and added 25 RT64 triangle-parse
join rows. Zero-shade task 193 rows on child DLs 0x4B7930 and 0x4B7BE8 all
carried the same last F5 state (ordinal 30, source 0x7403A8), so the join is
still child-DL-shaped rather than source-specific.

HYPOTHESIS-ID: m4-zero-shade-source-consumer-join

## One work unit

Add a bounded event-order trace in the regeneration-owned F5 probe and the
RT64 triangle parser. Assign a task-local sequence to every F5 VTXCOLOR update
and log that sequence/source at each emitted RDP triangle parse, retaining the
existing shade serial/range and `[tri-source-join]` rows. Do not add a
mitigation or hand-edit generated files. Export submodule patches after the
RT64 edit.

Competing hypotheses and discriminating measurement:

- `H-triangle-source-join`: an ordered F5 update sequence immediately before
  the relevant triangle identifies the source update feeding a zero-shade
  replacement.
- `H-child-range-only`: the sequence remains constant across child DLs or
  changes only at child-DL boundaries, leaving only child association.
- `H-triangle-source-missing`: no valid ordered F5 event is visible at the
  triangle parser, despite positive controls.

The discriminating table must key task, root DL, F5 event sequence,
VTXCOLOR ordinal/source/PC, triangle emission order, submit serial/range,
RT64 DL, and shade ordinal. It is invalid unless VI-1024, generated-write,
F5-state, accepted-range, triangle, range-bearing shade, and both positive and
zero-shade controls fire in the same gated phase.

Exact launch recipe:

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VTX_GENERATED_WRITES=1 ROGUESQ_LOG_VTX_WRITE_FAULT=1 ROGUESQ_LOG_F5_STATE=1 ROGUESQ_LOG_SHADE_RAW=1 ROGUESQ_LOG_TRI_WRITER=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a' zsh tools/probe.sh scratch/agent/s1007_f5_event_order_20260814 180 3`

An ordered source-specific match selects `H-triangle-source-join`; constant
state across child DLs selects `H-child-range-only`; absent or unstable event
state selects `H-triangle-source-missing`. If any control fails, record the
capture as invalid and make no causal selection.
