# Next work unit: requalify the four-arm M5 route with a new schedule discriminator

HYPOTHESIS-ID: m5-route-schedule-discriminator-4030

Competing hypotheses:

- H1: rotating the launch order changes the pre-target crash outcome, so the
  old failure is schedule-sensitive.
- H2: the same arm-specific route failure recurs despite the schedule change,
  supporting an arm/path-specific defect.
- H3: all four arms qualify again, leaving the old crash unevaluated rather
  than causal.

Discriminator: run the same four arms concurrently but rotate launch order so
declared/real is not the first port arm, while keeping the retail oracle and
all phase/RSP/audio controls. H1 is a changed crash/phase outcome tied to
order; H2 is recurrence in the same arm/path independent of order; H3 is
qualification of every arm with no crash/abort. A single arm failure is not
enough to claim audio causality.

Exact commands: after adding the launch-order parameter to the existing
four-arm driver as the bounded part of this work unit:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env RS64_LAUNCH_ORDER=legacy-real,declared-silent,declared-real zsh scratch/agent/run_s4030_m5_route_requal.sh
```

Record the retail positive control, both target VIs, RSP/audio controls, each
arm's staging size, crash marker, and last guest PC in one comparison table.
Only resume the `0x800052AC` writer census if all required controls qualify.
