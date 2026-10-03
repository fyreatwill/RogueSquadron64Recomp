# Next work unit: image-only alternate-object boundary

HYPOTHESIS-ID: m5-alternate-object-image-only

The s3773 image-first paired qualification remained unevaluable: oracle
controls passed, image reached title and hangar, and silent crashed before
target. The paired arm-order experiment is parked after s3771–s3773. Run one
image-only port arm beside the retail oracle using the existing clear/object
and family-edge instrumentation. Do not add fields, change the clear, inject
values, or change an audio gate. The image-only result cannot be used to claim
an image-versus-silent difference.

Competing hypotheses and the discriminating measurement:

- H1: S/L alternate stores belong to the legitimate clear-associated asset
  object; predicted `clear_span=1` with a stable `clear_obj`.
- H2: S/L stores belong to a distinct object/route and the route handoff is
  mismatched; predicted `clear_span=0` with stable clear and route identities.
- H3: I's missing hangar stores are an absent hangar edge; predicted I hangar
  rows or a positive I call edge with no generated store.

The discriminator is one image-only capture with the retail whole-RDRAM
positive control, image family controls, and both image target VIs. Compare
`clear_span`, `clear_obj`, route ordinal, and I hangar/call-edge rows. The
missing silent arm is a qualification limitation, not a null result.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3773_m5_image_only.sh

Expected outcomes:

- `clear_span=1` with stable `clear_obj` supports a legitimate alternate
  asset object, subject to later paired-control validation.
- `clear_span=0` with stable clear and route identities keeps route/object
  mismatch live.
- I hangar rows, or a positive I call edge with no generated store, selects
  the I hangar-edge hypothesis.
- Missing oracle control, family control, or either target VI is unevaluable;
  do not update the hypothesis table from it.
