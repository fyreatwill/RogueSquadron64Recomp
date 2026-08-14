# NEXT work unit (s1022)

HYPOTHESIS-ID: m4-zero-shade-accumulator-origin

Perform one bounded offline analysis of the valid corrected s1022 capture
`scratch/agent/soak_results/s790_postsec2_reachability_20260814-024858/run.log`.
Pair stage 10, 11, and 12 rows by invocation order and count, for each lane,
whether stage-12 `v6` equals stage-11 `v6` or stage-11 `v29`. Report any
0x8000 endpoint and whether it is present before VMADH, created by VMADH, or
selected by VGE. Do not launch another game run in this work unit.

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

Exact command shape (read-only; use an awk/Python one-shot, no file writes):

    rg '\[m4-accum\]' scratch/agent/soak_results/s790_postsec2_reachability_20260814-024858/run.log | ...

Required output: separate stage-1 controls from stage-10/11/12 M4 rows and
give a discriminator result or explicitly state why tuple pairing is
insufficient.
