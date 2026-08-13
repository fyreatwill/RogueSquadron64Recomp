# NEXT work unit (classify late E9 parser/filter versus join population)

HYPOTHESIS-ID: m3-e9-parser-filter-join

Perform one bounded source-and-log accounting audit of the now-keyed late
population. Do not change runtime behavior or add a mitigation. Enumerate
every producer and consumer of `g_task_bridge_e9`, `s_rdp_advance_task_e9`,
`g_e9prov.aligned`, and the task-join begin/end snapshots; then reconcile the
same late task IDs (570–649) against the s833 log by serial, [lo,hi), and
epoch. Use the existing source locations and one computed log summary; no
new build or soak is needed unless the audit finds an uninstrumented writer.

Competing hypotheses and the discriminating measurement:

- H-parser-filter: producer/consumer ranges and task identity are aligned, but
  the authoritative RT64 parser counter intentionally or accidentally filters
  E9-bearing ranges before the join snapshot.
- H-join-population: the apparent delta mismatch is created by different task
  populations or snapshot lifetimes despite matching submit/consumer serials.
- H-counter-ownership: one of the counters is cumulative, reset at a different
  lifecycle boundary, or updated on a second path, so equal values are not
  comparable even with matching task IDs.

Discriminator: the audit must produce an exhaustive writer/reset table and a
per-task reconciliation for all late aligned rows. If every aligned row has
the same task/epoch and exact producer/consumer range evidence while parser
increments are absent or lower on a traced path, select H-parser-filter. If
the join rows combine different task epochs/populations, select
H-join-population. If a second writer/reset boundary exists, select
H-counter-ownership. A partial inventory is unevaluable.

Expected commands: `rg -n` the four symbols in `src/` and `lib/rt64/`, inspect
bounded windows around every hit, then run a short parser over
`scratch/agent/soak_results/s833_e9_submit_budget_20260813-041100/run.log` to
emit counts for late submit/consumer exact matches, aligned joins, and epoch
consistency. Record the selected branch and any remaining uncertainty; do not
rerun the game.
