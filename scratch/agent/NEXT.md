# NEXT work unit (late aligned-task producer serial coverage)

HYPOTHESIS-ID: m3-e9-consumer-ordering

Make one bounded telemetry-only change to retain submit serial/range records
for the late aligned population (the current 128-row budget ends at task 282),
then build and run one phase-gated capture with the existing recipe. Keep game
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
- H-telemetry-budget: the late mismatch is real, but the current producer log
  budget hides the serial/range evidence needed to test it.

Discriminator: at VI 1024, with late `[e9-submit-range]` rows retained, key
`[e9-submit-range]` and `[e9-consumer-range]` by serial and [lo,hi), then join
them to the same late `[e9-task-join]` task. Equal serial/ranges with unequal
late deltas selects parser/filter or join-population; divergence implicates the
submit path. A run without VI 1024 or without positive controls is unevaluable.

Expected commands: inspect the submit log budget, patch only that budget,
confirm the recipe/env, then
`cmake --build build --config Debug --target RogueSquadron64Recomp` and run the
single selected recipe from `build/` with SIGKILL watchdog behavior. Inspect
bounded marker slices and record the result; do not run repeat soaks manually.
