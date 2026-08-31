# NEXT work unit — join qualified retail writers to one port capture

HYPOTHESIS-ID: m5-state-pointer-producer

Session 3472 qualified the retail physical table-span writer schema. The
whole-RDRAM control and title phase fired, candidate writers were observed,
and post-store values were nonzero. Exact writer-to-selected-entry identity
is still open; the port already has regeneration-safe table-selection,
state-pointer, and output/state witnesses.

Competing hypotheses and discriminating outcomes:

- `H-RetailStateWriter`: the port's selected-entry/value rows differ from the
  qualified retail producer values before the divergent consumer tuple.
- `H-PortPointerSelection`: the port reproduces the qualified producer/value
  family but selects a different state pointer before the consumer.
- `H-PortObservationInvalid`: the existing port schema/control fails to emit
  a title row, so the cross-runtime join remains unevaluable.

Discriminating measurement: run one image-arm port capture with
`ROGUESQ_LOG_M5_TABLE_SELECTION=1`, `ROGUESQ_LOG_M5_STATE_POINTER=1`, and
`ROGUESQ_LOG_M5_OUTPUT_STATE_FIELDS=1`, then join the selected table entries,
state-pointer checkpoints, and four-PC consumer rows by the in-run phase
ordinal. A live port control plus matching retail value family but different
selected pointer selects `H-PortPointerSelection`; a live control plus a
different selected/value family selects `H-RetailStateWriter`; absent port
control or rows selects `H-PortObservationInvalid`.

Work unit: one port image-arm run using the already-built witnesses; no new
instrument build is needed. Run from `build/`, kill with SIGKILL after the
capture window, and retain the complete log under
`scratch/agent/s3473_m5_port_state_join/`. Do not compare sequential animated
arms. Do not alter audio waits, slots, status handling, consumer dispatch,
clear behavior, or PCM writeback.

Exact preparation command:

`mkdir -p scratch/agent/s3473_m5_port_state_join && cd build && env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a' PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_TABLE_SELECTION=1 ROGUESQ_LOG_M5_STATE_POINTER=1 ROGUESQ_LOG_M5_OUTPUT_STATE_FIELDS=1 ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp > ../scratch/agent/s3473_m5_port_state_join/run.log 2>&1 & pid=$!; sleep 80; kill -KILL "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true`

Expected outcomes: a live port control plus matching retail value family but
different selected pointer selects `H-PortPointerSelection`; a live control
plus different selected/value family selects `H-RetailStateWriter`; absent
port control or target rows selects `H-PortObservationInvalid`. No mitigation
or runtime behavior change is authorized by this unit.

Evidence baseline: `scratch/agent/s3472_retail_state_writer_postvalue.log`,
`scratch/agent/s3471_m5_port_tuple/run.log`,
`docs/M5-S3471-OUTPUT-STATE-TUPLE.md`, and
`docs/M5-S3469-PORT-TABLE-SELECTION.md`.
