# Next work unit: clear-object/I-edge join on qualified image arm

HYPOTHESIS-ID: m5-clear-object-edge-join

The s3776 probe split qualified the writer-setup witness: control and probe
both reached title and hangar with the oracle and family controls, while the
family-edge control remained absent. The next unit is one image-only capture
beside the retail oracle using the repaired clear-edge harness and writer
setup logging enabled.

Competing hypotheses and the discriminating measurement:

- H1: family stores belong to the clear-associated object; predicted clear
  allocation identity joins S/L/I stores and family-edge rows appear in target
  phases.
- H2: stores belong to a legitimate alternate object; predicted target stores
  remain outside the clear object while writer setup and edge rows identify the
  alternate route.
- H3: the clear/edge witness is still not reached or route identity differs;
  predicted positive controls and target VIs pass but clear-object or edge rows
  remain absent, making the join unevaluable.

The discriminator is the aligned target-phase table of clear-object identity,
span membership, family-store destination, and family-edge rows. Missing rows
are an unevaluable outcome, not proof of H2.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3773_m5_image_only.sh

Expected outcomes:

- Clear object joins family stores: classify their destination as clear-object
  or alternate and proceed to the route-legitimacy question.
- Clear object does not join but edge rows identify another route: select H2
  only if the alternate route is independently identified as legitimate.
- Positive controls and target VIs pass but joins/edge rows remain absent:
  select H3 and redesign the witness; do not add a mitigation.
