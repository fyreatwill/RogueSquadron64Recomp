# Next work unit: fresh M5 route qualification under launch-gap permutation

HYPOTHESIS-ID: m5-route-schedule-discriminator

Competing hypotheses:

- H1: the legacy/real pre-target crash is caused by launch timing/order; a
  changed permutation or gap lets legacy/real reach both target phases.
- H2: the failure is arm-specific and persists despite the new schedule;
  declared/real and/or silent remain the only qualifying arms.
- H3: the route is nondeterministic or the recipe is invalid; the independent
  retail controls or required port phase controls fail, so no causal route
  conclusion is allowed.

Discriminator: one same-build retail run plus all three port arms from
`run_s4028_m5_route_requal.sh`, launched in the new order
`legacy-real,declared-real,declared-silent` with a 15-second gap between arm
starts. Retail whole-RDRAM, title VI 1024, and hangar VI 512 controls must
fire; each port arm's RSP-source control and target-phase controls must be
recorded. Legacy reaching both phases selects H1. A repeatable pre-target
legacy failure with other arms qualified selects H2. Missing controls selects
H3.

Exact commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env RS64_BOUNDARY_OUT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s4039_m5_route_requal RS64_LAUNCH_ORDER=legacy-real,declared-real,declared-silent RS64_LAUNCH_GAP_SEC=15 zsh scratch/agent/run_s4028_m5_route_requal.sh
```

Capture all four logs and SIGKILL every arm through the recipe cleanup. Do not
run another candidate census until this route table qualifies.
