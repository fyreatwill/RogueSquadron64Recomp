# Next work unit: requalify the four-arm M5 route with a ten-second launch gap

HYPOTHESIS-ID: m5-route-schedule-discriminator-4032

Competing hypotheses:

- H1: a ten-second gap changes which arm reaches the target again, confirming
  that process-start timing is a route discriminator.
- H2: the five-second result recurs, so the split is tied to the tested arm/path
  condition rather than the launch gap.
- H3: all three port arms qualify, closing the route blocker and permitting the
  next source-writer census.

Discriminator: build once and run the retail oracle plus all three port arms in
the order `legacy-real,declared-silent,declared-real`, with a ten-second gap
between port launches. H1 is a changed qualifying arm or crash outcome versus
the five-second capture; H2 is recurrence of legacy/real and declared/real
pre-target crashes with declared/silent qualification; H3 is qualification of
every port arm. The retail positive control and both VI controls must fire. A
single arm failure does not establish audio causality.

Exact commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env RS64_LAUNCH_ORDER=legacy-real,declared-silent,declared-real RS64_LAUNCH_GAP_SEC=10 zsh scratch/agent/run_s4028_m5_route_requal.sh
```

Record the retail positive control, title/hangar phases, RSP/audio controls,
each arm's staging size, crash marker, and last guest PC in one comparison
table. Only resume the `0x800052AC` writer census if all required controls
qualify.
