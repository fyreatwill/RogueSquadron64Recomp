# Next work unit: fresh M5 route qualification under order/gap permutation

HYPOTHESIS-ID: m5-route-schedule-discriminator

Competing hypotheses:

- H1: launch order/gap controls scheduler interleaving; a new permutation lets a different port arm reach both target phases.
- H2: one or more declared/real or declared/silent arms fail before target independently of schedule; the split persists with the new permutation.
- H3: the recipe is invalid or the route is nondeterministic; retail controls or required port controls fail, so no causal route conclusion is allowed.

Discriminator: one same-build retail run plus all three port arms from
`run_s4028_m5_route_requal.sh`, launched in the new order
`declared-silent,legacy-real,declared-real` with a 20-second gap. Retail
whole-RDRAM, title VI 1024, and hangar VI 512 controls must fire; each port
arm's RSP-source control and target-phase controls must be recorded. A new
arm reaching both phases selects H1. A repeatable pre-target failure with
other arms qualified selects H2. Missing controls selects H3.

Exact commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env RS64_BOUNDARY_OUT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s4040_m5_route_requal RS64_LAUNCH_ORDER=declared-silent,legacy-real,declared-real RS64_LAUNCH_GAP_SEC=20 zsh scratch/agent/run_s4028_m5_route_requal.sh
```

Capture all four logs and SIGKILL every arm through the recipe cleanup. Do not
run another candidate census until this route table qualifies.
