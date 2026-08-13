# NEXT work unit (task-scoped E9 population join)

HYPOTHESIS-ID: m3-postsec2-authoritative-e9

Make one bounded diagnostic change, regenerate/build using the normal project
pipeline, and run one phase-gated post-sec2 capture. Do not change game logic
or add a mitigation. Add task-scoped telemetry that records, at the same LLE
task boundary, (1) bridge-submitted E9 delta, (2) authoritative RT64-parser
E9 delta, and (3) the existing inline-data-aware `e9_aligned` value. Keep the
positive provenance controls and VI-1024 phase gate. Scope logs to the target
phase and include a positive control row in the same run.

Competing hypotheses:

- H-bridge-parser-match: task-scoped bridge and parser E9 deltas agree, while
  the guest walker differs; the old discrepancy was mostly population scope.
- H-bridge-parser-loss: bridge E9 deltas exceed parser E9 deltas on the same
  task boundary; loss remains between DPC submission and authoritative parse.
- H-join-defect: the new same-boundary values cannot be joined or one delta is
  reset at a different boundary; the telemetry path is still defective.

Discriminating measurement: a positive-control task and post-sec2 task rows
with all three values on the same task serial. Matching bridge/parser deltas
select H-bridge-parser-match; a repeated bridge>parser delta selects
H-bridge-parser-loss; missing or boundary-inconsistent rows select
H-join-defect and require fixing the telemetry before interpreting parser
reachability.

Before building, write the exact producer/reset/join sites and the expected
outcome for each hypothesis in this file. Then use the repository's normal
regeneration order (`make_elf.py` -> N64Recomp -> `fixup_game_funcs.py` ->
cmake), run from `build/` with SIGKILL watchdog, and retain the existing
positive controls.
