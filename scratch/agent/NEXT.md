# NEXT work unit (s1023)

HYPOTHESIS-ID: m4-zero-shade-accumulator-origin

Run one corrected phase-gated M4 capture with a larger phase-scoped accumulator
row budget, keeping the independent stage-1 VMADH control enabled. Pair stage
10, 11, and 12 rows by invocation order and classify any 0x8000 endpoint as
pre-existing, VMADH-created, or VGE-selected. Do not land a mitigation.

Competing hypotheses and discriminator:

- `H-accumulator-saturation`: the endpoint shade is created by VMADH saturation.
- `H-v4-v0-arithmetic`: the endpoint is an ordinary bounded VMADH result.
- `H-v29-selection`: VGE selects a threshold-table lane matching the sentinel.

The discriminator is the complete pre/post accumulator tuple from the
independent VMADH positive control and live M4 rows. Endpoint lanes already
present before VMADH select ordinary arithmetic; endpoint lanes created only by
saturation select saturation; a matching v29 lane selects threshold selection.
A zero M4/control result is invalid unless the same run visibly reaches
VI-1024 and logs the positive controls. The s1022 offline result is only that
25 complete triplets had no endpoint; it did not select a hypothesis.

Exact preparation: inspect the existing s1022 capture recipe and increase only
the M4 accumulator row budget (phase-scoped), then build once and run once from
`build/` with the same 1024-relative key schedule and
`ROGUESQ_LOG_M4_ACCUM=1`. Required controls are VI-1024, stage-1 VMADH rows,
and at least one post-gate M4 stage-10/11/12 triplet. If the recurring
`slotDispatcherIter+8592` crash occurs before an endpoint, report the capture
as unevaluable and do not infer from the null.

Exact command shape (read-only; use an awk/Python one-shot, no file writes):

    rg '\[m4-accum\]' scratch/agent/soak_results/s790_postsec2_reachability_20260814-024858/run.log | ...

Required output: separate stage-1 controls from stage-10/11/12 M4 rows and
give a discriminator result or explicitly state why tuple pairing is
insufficient.
