# NEXT work unit (s1021)

HYPOTHESIS-ID: m4-zero-shade-accumulator-origin

Run one corrected 1024-gated M4 accumulator capture now that the active
composite controls pass. Launch from `build/`, capture to a non-dot final path,
and SIGKILL the process after the fixed window.

Competing hypotheses and discriminator:

- `H-accumulator-saturation`: the endpoint shade is created by VMADH saturation.
- `H-v4-v0-arithmetic`: the endpoint is an ordinary bounded VMADH result.
- `H-v29-selection`: VGE selects a threshold-table lane matching the sentinel.

The discriminator is the complete pre/post accumulator tuple from the
independent VMADH positive control and live M4 rows. Endpoint lanes already
present before VMADH select ordinary arithmetic; endpoint lanes created only by
saturation select saturation; a matching v29 lane selects threshold selection.
A zero M4/control result is invalid unless the same run visibly reaches
VI-1024 and logs the positive controls.

Exact command:

    env ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_VI=1 ROGUESQ_LOG_VI_ARGS=1 ROGUESQ_LOG_DPC=1 ROGUESQ_LOG_RUNNER=1 ROGUESQ_LOG_SLOT_SP_GUARD=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' zsh scratch/agent/s790_postsec2_reachability.sh > scratch/agent/m4_accum_s1022.log 2>&1

Required controls: VI 1024, positive VMADH-control rows, and M4 rows. If any
control is absent, classify the capture as phase/control-invalid and do not
classify the three M4 hypotheses.
