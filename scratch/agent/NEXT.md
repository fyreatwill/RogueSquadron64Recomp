# NEXT work unit (s1027)

HYPOTHESIS-ID: m4-zero-shade-accumulator-origin

Bounded change: split the M4 probe budget so the independent stage-1 VMADH
positive control is capped separately (64 rows) while stage-10/11/12 M4 rows
retain a 2048-row phase-scoped budget. Keep the probe sites and all runtime
semantics unchanged. This is the highest-information follow-up because the
s1026 shared 2048 cap stopped after task 79 while consuming 598 rows on the
stage-1 control, leaving only 483 rows per M4 stage.

Competing hypotheses and discriminator:

- `H-accumulator-saturation`: a later live shade tuple creates `0x8000` in
  `v6` or the relevant accumulator high/middle half at VMADH.
- `H-v4-v0-arithmetic`: later shade tuples remain ordinary bounded VMADH
  results and do not create the sentinel.
- `H-v29-selection`: a later VGE selects a `v29` lane matching `0x8000`.

The discriminator is a complete stage-10/11/12 tuple from a task beyond the
s1026 shared-cap frontier. Endpoint first present in the pre/post VMADH
accumulator selects saturation; endpoint absent before VMADH but present in
stage-11 `v6` selects ordinary arithmetic; endpoint matching stage-11 `v29`
at stage 12 selects VGE. If VI-1024, input edges, the separately capped
stage-1 control, and at least 2048 M4 rows all pass but no endpoint appears,
the numeric hypotheses remain unevaluable and no conclusion is allowed.

Exact commands:

    cmake --build build --target RogueSquadron64Recomp -j2
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_LOG_INPUT=1 ROGUESQ_LOG_DPC=1 ROGUESQ_LOG_M4_ACCUM=1 \
      PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 \
      PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' \
      zsh tools/probe.sh scratch/agent/soak_results/s1027_m4_accum 512 0.5

Required controls are VI-1024, input edges, at least one stage-1 VMADH
positive-control row, and at least 2048 M4 rows with complete triplets.
Analyze the log with a read-only one-shot; do not infer from a missing
endpoint unless every control and the later-task coverage condition pass.
