# Next work unit: bisect why the s5099 hangar recipe fails on the 18:30 binary
HYPOTHESIS-ID: patcheslib-shadowed
s5373 control (s5099 recipe verbatim, current 18:30 binary): title reached, hangar 0/2, no crash. Env delta of s5371 is cleared.
Hypotheses: H1 the 18:30 build regressed title->hangar (candidates 2bb94123 PatchesLib host decl/CMake, 8c27834d+6392e160 dpc_bridge M4 keys, s5368/s5370 census patches); H2 host focus/key delivery changed (winctl).
Discriminating measurement, ONE iteration: `git worktree`-free approach — copy the repo state at the commit just after s5099 (git log --since='2026-10-17 01:00' to find it) into a separate build dir (no git checkout in place; no lib/ touches; use `git archive` for src/tools/CMake and reuse lib/), build it, then run the s5099 recipe on BOTH binaries (old, new), each with the same recipe, one game at a time, 3 tries each.
- old reaches hangar, new does not: H1; bisect the listed commits.
- both fail: H2; investigate winctl activate / key delivery (positive control: key press visibly changes the title screen).
- both pass: flaky host; rerun.
