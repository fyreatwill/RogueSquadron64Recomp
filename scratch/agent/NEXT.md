# NEXT work unit (s1026)

HYPOTHESIS-ID: m4-zero-shade-accumulator-origin

Bounded change: raise the phase-scoped `rs64_m4_accum_probe` cap from 512 to
2048, then run one corrected LLE capture with the full phase-relative schedule.
Do not add a mitigation or change the probe sites. The purpose is to sample
later Factor 5 tasks after the valid s1025 controlled null.

Competing hypotheses and discriminator:

- `H-accumulator-saturation`: a later live shade tuple creates `0x8000` in
  `v6` or the relevant accumulator half at VMADH.
- `H-v4-v0-arithmetic`: later shade tuples remain ordinary bounded VMADH
  results and do not create the sentinel.
- `H-v29-selection`: a later VGE selects a `v29` lane matching `0x8000`.

The discriminator is a complete stage-10/11/12 tuple containing a shade
endpoint: endpoint first present in the post-VMADH accumulator selects
saturation; endpoint absent before VMADH but present in stage-11 `v6` selects
ordinary arithmetic; endpoint matching stage-11 `v29` at stage 12 selects VGE.
If the independent stage-1 control, VI-1024, and input edges pass but no
endpoint appears, the numeric hypotheses remain unevaluable and no conclusion
about the sentinel is allowed.

Exact commands:

    cmake --build build --target RogueSquadron64Recomp -j2
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_LOG_INPUT=1 ROGUESQ_LOG_DPC=1 ROGUESQ_LOG_M4_ACCUM=1 \
      PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 \
      PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' \
      zsh tools/probe.sh scratch/agent/soak_results/s1026_m4_accum 512 0.5

Required controls are VI-1024, input edges, stage-1 VMADH rows, and at least
one complete M4 triplet. Analyze the log with a read-only one-shot; do not
infer from a missing endpoint unless all four controls are present.
