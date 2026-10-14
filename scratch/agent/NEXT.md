# Resume next work unit

HYPOTHESIS-ID: m5-step11-clear-discriminator

Single bounded work unit: add one independent, phase-scoped clear-site
discriminator for the second MusyX wait, rebuild once, and run the same-build
default / `ROGUESQ_AUDIO_SPIN2_YIELD=0` pair. The current logger's arm and loop
rows fire, but its expected `waitmusyx-spin2-clear` row is absent in both arms;
do not repeat the prior A/B unchanged.

Competing hypotheses:

* H-clear-site-unreached: the guest never executes the expected
  `0x800912F4`/`0x8014974C` clear store on the qualified title/hangar route.
* H-clear-site-anchor-drift: the clear store executes, but the fixup anchor no
  longer matches generated code, so the logger is absent while the gate still
  changes.
* H-clear-site-other-writer: a different instruction or thread clears the
  legitimate `0x8014974C` gate, so the current named-site logger is incomplete.
* H-route-regressed: the route-stabilizing tuple no longer reaches the same
  phase-5 wait, disproving the positive controls needed to interpret a null.

Discriminating measurement: in each arm and phase-5 route join, record one
bounded table containing (1) execution of the expected guest-PC clear store,
(2) gate-byte value immediately before and after that store, (3) all observed
writes to physical/RDRAM `0x8014974C` with guest PC and thread, and (4) the
existing arm/loop/return rows. A positive task/SP + nonzero PCM + title/hangar
control is mandatory. Expected outcomes: expected-PC execution with a 1->0
transition selects H-clear-site-anchor drift only if the old logger is absent;
no expected-PC execution but another writer's 1->0 selects H-clear-site-other-
writer; no clear writer in either arm selects H-clear-site-unreached; missing
phase controls selects H-route-regressed.

Preparation: update the vendored fixup source (not generated output) with the
single table above, keeping all rows phase-scoped; build
`cmake --build build --config Debug --target RogueSquadron64Recomp`; run
`zsh tools/run_m5_yield_ab.sh` from the repo root. Keep
`ROGUESQ_STUB_MISSING_FUNCS=1`, LLE force/ungated/solo, host spin yield, and
SIGKILL cleanup. Do not interpret any clear null without the `[m5-gate]`, VI,
SP, and nonzero PCM controls.
