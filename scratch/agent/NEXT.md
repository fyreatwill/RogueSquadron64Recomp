# Next work unit: requalify the four-arm M5 route before resuming source census

HYPOTHESIS-ID: m5-route-requalification-4028

Competing hypotheses:

- H1: the current route is qualified; retail and declared/real,
  declared/silent, and legacy/real all reach title VI 1024 and hangar VI 512
  in one same-build capture with their RSP/audio controls and no crash/abort.
- H2: one audio arm is causally route-breaking; its phase/control pattern or
  crash differs from the other arms.
- H3: the route result is schedule-sensitive or otherwise unevaluable; at
  least one port arm fails before the target phases without a reproducible
  arm-specific discriminator.

Discriminator: run all four arms concurrently in one capture. Retail's
whole-RDRAM positive control, title/hangar VI controls, each port arm's
`m5-rsp-source-hook-control` and audio-stage control, target phases, and
crash/abort markers must be summarized per arm. H1 requires all arms to reach
both target phases without crash/abort; H2 requires a repeatable arm-specific
failure; H3 is the result when a port arm fails without that separation.

Exact commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s4028_m5_route_requal.sh
```

The new script must be self-contained and launch retail plus declared/real,
declared/silent, and legacy/real concurrently, use the established
phase-gated controls from `scratch/agent/run_s4015_m5_scheduler_spin_split.sh`,
and SIGKILL all children in cleanup. Do not resume the `0x800052AC` census or
change audio behavior until this four-arm discriminator is reported.
