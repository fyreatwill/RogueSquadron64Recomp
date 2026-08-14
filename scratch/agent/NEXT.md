# NEXT work unit (s1024)

HYPOTHESIS-ID: m4-zero-shade-accumulator-origin

Reproduce the known s1022 M4-positive path with the 512-row budget, using the
full phase-relative input schedule and simultaneous input/DPC/M4 logging. First
prove the active Factor 5 task path reaches the stage-1 control; only then pair
stage 10/11/12 rows and classify any 0x8000 endpoint. Do not land a mitigation.

Competing hypotheses and discriminator:

- `H-accumulator-saturation`: the endpoint shade is created by VMADH saturation.
- `H-v4-v0-arithmetic`: the endpoint is an ordinary bounded VMADH result.
- `H-v29-selection`: VGE selects a threshold-table lane matching the sentinel.

The numeric discriminator is the complete pre/post accumulator tuple from the
independent VMADH positive control and live M4 rows. Endpoint lanes already
present before VMADH select ordinary arithmetic; endpoint lanes created only by
saturation select saturation; a matching v29 lane selects threshold selection.
A zero M4/control result is invalid unless the same run visibly reaches
VI-1024, logs input edges, and proves the active Factor 5 task path with the
stage-1 control. The s1024 full-schedule null failed that last control and did
not select a hypothesis.

Exact preparation: use one build and one run from `build/` with
`ROGUESQ_LOG_INPUT=1`, `ROGUESQ_LOG_DPC=1`, and `ROGUESQ_LOG_M4_ACCUM=1`,
`PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, `PROBE_LEAVE_OK=1`, and
`PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start'`.
Required controls are VI-1024, observed input edges, stage-1 VMADH rows, and
at least one post-gate M4 triplet. If stage-1 is absent, classify the active
task/ucode path as unreached and do not infer from the numeric null.

Exact command shape (read-only; use an awk/Python one-shot, no file writes):

    rg '\[m4-accum\]' scratch/agent/soak_results/s790_postsec2_reachability_20260814-024858/run.log | ...

Required output: separate stage-1 controls from stage-10/11/12 M4 rows and
give a discriminator result or explicitly state why tuple pairing is
insufficient.
