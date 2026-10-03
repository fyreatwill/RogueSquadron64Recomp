# Next work unit: split probe-induced versus route pre-target crash

HYPOTHESIS-ID: m5-clear-edge-probe-perturbation

The repaired s3774 harness added `ROGUESQ_LOG_M5_WRITER_SETUP=1`, but its
image arm crashed before target and before both the writer-setup and family-
edge controls. The prior image-only recipe reached both target VIs. This
creates a new, testable possibility that the added witness perturbs the route.

Competing hypotheses and the discriminating measurement:

- H1: writer-setup logging perturbs execution; predicted probe-off reaches both
  target VIs while probe-on reproduces the pre-target crash.
- H2: the crash is route instability unrelated to the witness; predicted both
  same-build image arms have the same reach/crash class.
- H3: the prior target qualification was an unrepeatable transient; predicted
  both arms reach target and reproduce the clear/edge control gap.

The discriminator is one same-build concurrent capture with two image arms,
one with `ROGUESQ_LOG_M5_WRITER_SETUP=0` and one with it enabled, plus the
retail oracle. Compare target-VI reach, crash PC, family-store controls,
writer-setup controls, and family-edge controls. Missing target/control rows
remain unevaluable for that arm; do not infer clear/object legitimacy.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3775_m5_probe_split.sh

Expected outcomes:

- Only probe-on crashes pre-target: select H1 and redesign the witness.
- Both arms share the crash class: select H2 and keep the clear-edge join
  pending for a route-stabilizing discriminator.
- Both arms reach target with positive controls: select H3 and resume the
  clear-object/I-edge join using the qualified arm.
