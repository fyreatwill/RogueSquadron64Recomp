# Next work unit: qualify clear object and I call edge

HYPOTHESIS-ID: m5-alternate-object-clear-edge-qualification

The s3774 image-only run passed oracle/family/title/hangar controls, but the
clear object was zero and the family-edge instrumentation emitted no rows.
S/L alternate destinations and I's missing hangar stores therefore cannot be
joined to the clear object or an I call edge. The paired arm-order experiment
is parked after s3771–s3773.

Competing hypotheses and the discriminating measurement:

- H1: the existing join is phase/initialization blind; predicted positive
  clear object/length and positive I edge controls after changing only the
  qualification gate.
- H2: the clear/object join is genuinely absent in the image route; predicted
  positive clear control but `clear_span=0` on S/L rows.
- H3: I's missing hangar stores are an absent hangar edge; predicted positive
  I call edge with no hangar generated stores.

The discriminator is one image-only capture with the retail whole-RDRAM
positive control, image family controls, both target VIs, a nonzero
clear-object/length control, and a positive I call-edge control. Compare
`clear_span`, `clear_obj`, route ordinal, and I hangar/call-edge rows. If any
required control is absent, the result is instrumentation-unevaluable, not
evidence for H2/H3. The missing silent arm is still a qualification
limitation, not a null result.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3774_m5_clear_edge.sh

Expected outcomes:

- Positive clear and I-edge controls with `clear_span=1` support a legitimate
  alternate asset object, subject to later paired-control validation.
- Positive clear control with `clear_span=0` keeps route/object mismatch live.
- A positive I call edge with no hangar store selects the I hangar-edge
  hypothesis.
- Missing oracle control, family control, either target VI, clear control, or
  I-edge control is unevaluable; do not update the hypothesis table from it.
