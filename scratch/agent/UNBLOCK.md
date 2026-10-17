# UNBLOCK s5247
Route taken: 1 (refute) + 3 (re-scope).
Block claimed: need permission for `cp -c -R` clone to build the old-commit (70a56647) arm.
Evidence: the clone is only needed if the HEAD arm (soak_queue/s5246_head_arm_loadlog.sh) fails again.
That script is queued and has NOT run (no soak_results/s5246_head_arm_loadlog, absent from SOAK-RESULTS.md).
So the dependency was premature: the discriminating next observation (HEAD arm under logged host load) needs no clone.
Fallback if HEAD arm fails and cp stays denied: `git worktree add scratch/wt_70a56647 70a56647` (git, not cp; untested) with lib/ symlinked read-only. Human one-liner remains in BLOCKED.resolved.s5246-bisect-clone.md.
