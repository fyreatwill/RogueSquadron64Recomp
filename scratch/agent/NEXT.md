# NEXT: repair the G1 coverage queue launch contract

HYPOTHESIS-ID: g1-mission-coverage

Work unit: inspect the queued level-coverage scripts and make the smallest
bounded fix that restores a real launch. The last queue attempt produced
`g1_level_coverage_common rc=1, 0s` and `g1_lvl10a rc=127, 0s`; it was not a
mission result. Do not run a game experiment until the launch failure is
understood and the script repair is complete.

Competing hypotheses:

- H1: the common runner was deleted or moved before the recipe invoked it;
  the fix is to restore/update the recipe's path.
- H2: the recipe invokes a missing executable or shell helper; `rc=127` and
  the common script's stderr identify the unresolved command.
- H3: the recipe is launched from the wrong working directory or violates the
  required zsh re-exec guard; the fix is path/cwd/shell normalization.
- H4: the queue runner's consume/move step removed the first recipe while
  leaving later paired scripts; this is queue bookkeeping, not a launch bug.

Discriminator: inspect the exact scripts, their executable bits, the matching
`scratch/agent/soak_results/*g1*` logs, and queue/done paths in one pass. Each
outcome must identify whether the failure is a missing file, command (with its
stderr), cwd/shell contract, or queue bookkeeping. A valid repair must make a
syntax/path-only dry check succeed; only then queue/run the next two levels.

Suggested commands from the repository root:

```sh
sed -n '1,220p' scratch/agent/soak_results/g1_level_coverage_common_*.log
sed -n '1,220p' scratch/agent/soak_results/g1_lvl10a_*.log
for f in scratch/agent/soak_queue/g1_*.sh scratch/agent/soak_queue/done/g1_*.sh; do
  [ -f "$f" ] && { printf '%s\n' "--- $f"; sed -n '1,80p' "$f"; }
done
rg -n 'g1_level_coverage_common|g1_lvl10a|soak_queue/done|SOAK_TIMEOUT' tools scratch/agent
```

Expected split: if the common script or level-10 recipe is absent, restore the
queue recipe from the corresponding generator/template and document the exact
path; if a command is missing, fix that command/path; if bookkeeping consumed
it, repair queue placement without changing mission code. Then the next unit is
the first two valid level-coverage runs with `[lvsel]` positive controls.
