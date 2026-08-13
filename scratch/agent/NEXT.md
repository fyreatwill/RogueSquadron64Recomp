# NEXT work unit (late aligned-task serial capture)

HYPOTHESIS-ID: m3-e9-consumer-ordering

Run one phase-gated capture using the new bridge-submit/RT64-consumer serial
telemetry, with a recipe that demonstrably reaches VI width 1024. Keep game
logic, RDP behavior, and mitigation code unchanged. Before building, verify
the recipe contains `ROGUESQ_LOG_RDP_ADVANCE=1` and all four provenance
positive-control markers; do not accept a run that stops at VI 640 as evidence
about the late population.

Competing hypotheses and the discriminating measurement:

- H-parser-filter-remains: late aligned tasks have producer E9 serial/range
  records that reach the consumer, but parser advancement remains lower.
- H-parser-join-population: the earlier mismatch joined different task
  populations; late producer/consumer/task joins will align or expose that.
- H-parser-writer-path: late producer serials/ranges diverge before the RT64
  consumer, implicating deferred/drop behavior.

Discriminator: at VI 1024, key `[e9-submit-range]` and
`[e9-consumer-range]` by serial and [lo,hi), then join them to the same late
`[e9-task-join]` task. Matching serial/ranges plus equal parser/bridge deltas
weakens the writer-path and parser-filter hypotheses; divergence implicates
the submit path. A run without VI 1024 or without positive controls is
unevaluable.

Expected commands: confirm the recipe/env, then
`cmake --build build --config Debug --target RogueSquadron64Recomp` and run the
single selected recipe from `build/` with SIGKILL watchdog behavior. Inspect
bounded marker slices and record the result; do not run repeat soaks manually.
