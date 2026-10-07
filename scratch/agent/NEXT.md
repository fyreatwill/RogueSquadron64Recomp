# Next work unit: audit the first voice/list/table guard idiom class

Maintenance completed in session 4118; no experiment was run. Resume this
single work unit next.

HYPOTHESIS-ID: m5-step8-voice-list-guard-class

Competing hypotheses and discriminator:

- H-guard-legitimate: every site in the selected idiom class protects a
  legitimate invalid pointer and is not suppressing valid audio work.
- H-guard-suppresses-valid: at least one guarded pointer has an independently
  attributed retail writer and a valid phase-scoped port range, so the guard
  can explain lost voice/list/table work.
- H-class-route-invalid: the paired capture misses a required control or target
  phase, so guard nulls are unevaluable and the class must not be relaxed.

The single discriminating measurement is one complete source census plus one
same-build retail/port phase-gated capture for the first ranked A10 guard
idiom class. Positive control must fire; retail must reach title and hangar;
the port must reach both phases; every guard site must be paired with its guest
writer, pointer value/range, and downstream traversal result. A retail writer
and valid port range at a guarded site selects H-guard-suppresses-valid; all
sites invalid or unreachable selects H-guard-legitimate; missing controls or
phases selects H-class-route-invalid. Do not remove or bypass any guard in
this unit.

Exact commands:

Before building, enumerate the first complete guard idiom and its writers with
bounded `rg` searches in the generated tree, fixup scripts, and oracle watch
configuration; then add all site/writer fields to one recipe and run it once.

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Use the existing retail positive-control and title/hangar phase-gate contract.
Do not land a behavior change unless the measurement selects
H-guard-suppresses-valid and the changed guard has an `ORIGIN:` naming the
writer and explaining why the value is legitimate.
