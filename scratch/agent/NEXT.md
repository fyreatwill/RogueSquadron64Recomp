# Next work unit: requalify the M5 route before resuming the parked writer census

HYPOTHESIS-ID: m5-route-qualification-4025

Competing hypotheses:

- H1: the route failure is schedule-sensitive; a same-build four-arm capture
  again reaches both target phases in declared/real, declared/silent, and
  legacy/real.
- H2: one audio mode or staging path is sufficient to reproduce the scheduler
  failure, splitting the arms before target phase.
- H3: the route remains intermittently unevaluable, with a missing target
  phase or crash/abort in at least one arm despite the controls.

Discriminator: one same-build capture of retail, declared/real,
declared/silent, and legacy/real using the existing route qualification
recipe. H1 requires retail whole-RDRAM/title/hangar/completion controls plus
both target phases and RSP/audio controls in all three port arms, with no
crash/abort. H2 requires a reproducible arm-dependent split tied to audio mode
or staging. H3 is any missing positive control, pre-target stall, or crash
without a stable arm-dependent split. Do not change audio behavior or add
candidate watches.

Commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s4019_m5_route_qualification.sh
```

Require the retail positive-control threshold, title VI 1024, hangar VI 512,
RSP/audio controls, and no `[CRASH]` or `[ABORT]` before resuming the parked
`0x800052AC` candidate class.
