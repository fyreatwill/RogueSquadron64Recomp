# NEXT work unit (s1891)

HYPOTHESIS-ID: vi1024-reachability-regression

**Status: BLOCKED.** See `scratch/agent/BLOCKED.md` for the full explanation
and exact commands. Do not attempt a 5th consecutive iteration re-confirming
the VI-1024 stall — s1888-s1890 already established and exhaustively
code-audited it (8/8 fresh runs fail, four crash/stall signatures, H1-flake
refuted, full s844-HEAD content diff audited with no explanation found, the
one real candidate `rs64_is_hangar_vi()` built and refuted). Nothing new can
be learned from this angle inside this harness without one of:

1. A machine-state snapshot (`top -l 1`, `vm_stat`, `who`, `pmset -g therm`,
   `sysctl -n hw.ncpu hw.memsize`) taken by a human OUTSIDE this harness and
   dropped at `scratch/agent/human_snapshot.txt` — tests H3-machine-state.
2. A disposable clone with `git submodule update --init --recursive` already
   run against commit `ef7a0fb9` (s844), left at (e.g.)
   `/tmp/rs64-bisect-clone` — enables the actual historical-commit bisect,
   which cannot run inside this worktree (`git submodule update` denied by
   command-string match regardless of directory).

## If a human has supplied (1) or (2) since this was written

Act on it directly:
- Snapshot supplied: read it, check for thermal throttling / memory pressure
  / competing processes around the 7-9s mark where all 8 prior runs stalled
  at VI 640 `0x00696100`. Compare against a snapshot taken during a
  known-good era if one exists; if not, at least rule out obvious resource
  exhaustion.
- Clone supplied: build the pre-s844 (`ef7a0fb9`) commit in that clone (same
  regen order: `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` ->
  `cmake`), run `s790_postsec2_reachability.sh` against it, and compare
  directly against a fresh HEAD run. This is the first same-recipe cross-commit
  A/B available since the regression was found — treat a VI-1024 reach on the
  old commit plus a stall on HEAD as the discriminating result closing H4 vs.
  H3 vs. an as-yet-unnamed H-environment-drift.

## If neither has materialized

Stay BLOCKED. Re-write `scratch/agent/BLOCKED.md` only if something material
changed (e.g. one ask was partially supplied); otherwise leave it as-is and
do not spend another iteration regenerating the same analysis. Only pick a
different work unit entirely (e.g. drop to strategic-priority item 4, the
generated-symbol renaming sweep, per `tools/agent/ITERATION.md`'s strategic
priority list) if the iteration-selection logic there explicitly allows
working around a BLOCKED top-priority item — check that document's current
wording before doing so, since this file does not override it.
