# NEXT work unit (task-scoped E9 join aggregation)

HYPOTHESIS-ID: m3-e9-callback-task-ownership

Run one bounded, read-only aggregation over the completed s825 capture. Join
each repaired `[e9-task-join]` row to its `[dl-sync-probe2]` task and classify
aligned guest E9 against bridge/parser deltas. Do not change runtime code or
rerun the game.

Competing hypotheses:

- H-task-scoped-parity: matched task rows show aligned, bridge, and parser
  counts agreeing; the earlier discrepancy was population/sampling scope.
- H-task-scoped-loss: matched rows show aligned E9 greater than parser E9;
  the discrepancy survives the repaired ownership join.
- H-join-sample-bias: repaired rows cover only controls or a narrow selected
  subset; there are too few matched post-sec2 rows to classify either count
  relationship.

Discriminating measurement: derive one table from
`scratch/agent/soak_results/s790_postsec2_reachability_20260813-031909/run.log`
using bounded `grep`/`awk` or a one-off read-only script, with control rows
separate from post-sec2 rows. Report matched task IDs and aligned/bridge/parser
counts. Expected outcomes are parity, a reproducible aligned>parser delta, or
insufficient matched post-sec2 coverage; do not infer parser loss from an
unjoined row.

No build command is expected for this work unit.
