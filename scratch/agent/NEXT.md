# Next work unit: requalify the four-arm M5 route with staggered launch timing

HYPOTHESIS-ID: m5-route-schedule-discriminator-4031

Competing hypotheses:

- H1: staggering launch timing changes the pre-target failure outcome, so
  process-start concurrency is schedule-sensitive.
- H2: the legacy/real arm still fails before target phases while declared/real
  reaches them, supporting an arm/path-specific defect independent of launch
  timing.
- H3: all three port arms qualify, leaving the prior failure unevaluated.

Discriminator: run the same four arms with the retail oracle and all
phase/RSP/audio controls, but launch the three port arms 2 seconds apart in
the order legacy-real, declared-silent, declared-real. H1 is a changed
legacy phase/crash outcome relative to s4030; H2 is recurrence of the
legacy-before-target failure while declared/real reaches hangar; H3 is
qualification of every port arm. A single arm failure is not enough to claim
audio causality.

Exact commands: add a 2-second launch gap to the existing four-arm driver as
the bounded part of this work unit, then:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env RS64_LAUNCH_ORDER=legacy-real,declared-silent,declared-real RS64_LAUNCH_GAP_SEC=2 zsh scratch/agent/run_s4028_m5_route_requal.sh
```

Record the retail positive control, both target VIs, RSP/audio controls, each
arm's staging size, crash marker, and last guest PC in one comparison table.
Only resume the `0x800052AC` writer census if all required controls qualify.
