# NEXT work unit — locate the port state-pointer writer edge

HYPOTHESIS-ID: m5-state-pointer-writer

Session 3473 joined the qualified port witnesses. Both controls fired; port
producer values included the qualified retail family `0x801B4F00` /
`0x801B5E70`, but downstream state pointers were `0x80110xxx` rather than
retail's qualified `0x801B1590`. The next boundary is the port-side writer or
transformation producing that pointer.

Competing hypotheses and discriminating outcomes:

- `H-InterveningPointerWriter`: a port store/load between producer input and
  consumer first creates the `0x80110xxx` state pointer.
- `H-AlternateDispatch`: no intervening pointer write exists; a different
  dispatch or object-selection edge supplies the pointer at the consumer.
- `H-PortObservationInvalid`: the batched instrument or phase gate fails to
  expose the intervening edge despite a live consumer control.

Discriminating measurement: ask the independent retail oracle first for the
candidate physical pointer-store span and PC set, then add all candidate
port-side store/load watches in one build and run with
`ROGUESQ_LOG_M5_TABLE_SELECTION=1`, `ROGUESQ_LOG_M5_STATE_POINTER=1`, and
`ROGUESQ_LOG_M5_OUTPUT_STATE_FIELDS=1`. Join producer value, first pointer
store/load, and consumer rows by the in-run phase ordinal. A live control and
first `0x80110xxx` store before the consumer selects
`H-InterveningPointerWriter`; a live control with no such store selects
`H-AlternateDispatch`; missing control or target rows is
`H-PortObservationInvalid`.

Work unit: one bounded oracle preflight for the physical candidate pointer
span, followed by one batched port instrumentation build and one image-arm
capture. Do not compare sequential animated arms. Do not alter audio waits,
slots, status handling, consumer dispatch, clear behavior, or PCM writeback.

Exact capture command (after the oracle candidate span and instrumentation
are prepared):

`mkdir -p scratch/agent/s3474_m5_pointer_writer && cd build && env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a' PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_TABLE_SELECTION=1 ROGUESQ_LOG_M5_STATE_POINTER=1 ROGUESQ_LOG_M5_OUTPUT_STATE_FIELDS=1 ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp > ../scratch/agent/s3474_m5_pointer_writer/run.log 2>&1 & pid=$!; sleep 80; kill -KILL "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true`

Expected outcomes: the first title-gated `0x80110xxx` pointer store/load
before a consumer selects `H-InterveningPointerWriter`; no intervening store
with a live consumer selects `H-AlternateDispatch`; missing controls are
unevaluable. No mitigation or runtime behavior change is authorized.
