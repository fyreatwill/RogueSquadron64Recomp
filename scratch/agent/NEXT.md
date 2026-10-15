# Next work unit

HYPOTHESIS-ID: m5-callback-teardown-reachability

Run one fresh, phase-gated callback-teardown reachability capture on the
qualified real-audio/LLE/ungated/solo/spin-yield route. Instrument or reuse the
existing callback entry/deregistration controls to distinguish whether
`shutdownAudioEngine` is entered, whether its callback-table deregistration
fires, and whether the route returns with task/SP, PCM, title, and hangar
controls. Do not repeat the completed A12 or synth-dedup A/B.

Competing hypotheses:

- H1: the callback teardown path is reached on this qualified route; entry,
  deregistration, and return rows form an ordered lifecycle with downstream
  controls.
- H2: the route never reaches `shutdownAudioEngine`; entry and deregistration
  are both absent despite positive route controls, so this boundary is parked.
- H3: teardown is entered but does not return or deregister correctly; a
  crash, hang, or missing ordered callback row identifies the live boundary.

Discriminator: one rebuilt binary and one phase-gated run with callback entry,
deregistration, return, task/SP, PCM, title/hangar, and crash/abort controls.
H1 selects a teardown lifecycle for the next boundary audit; H2 closes this
route as unqualified; H3 identifies a teardown defect requiring a new writer
and legitimacy audit. The prior A12 result is H2/route-neutral and is not
repeated.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LOG_S4700_CB=1 ROGUESQ_LOG_SP_TASKS=1 ROGUESQ_LOG_M5_ROUTE_ORDER=1 zsh <callback-teardown-recipe>

Do not start the generated-symbol sweep while this M5 unit is applicable.
