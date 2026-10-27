# NEXT: RESUME — deterministic FD57 capture-route audit
HYPOTHESIS-ID: g3c-owner-visual-b

This is the next work unit after the s6383 maintenance pass. Do not rebuild or
rerun s6380 before the offline audit. Do not treat the missing FD57 row as a
clamp result.

Compare these bounded artifacts:

- `scratch/agent/m6/g1_lvl2s6378/run.log` — known FD57 positive control
- `scratch/agent/m6/g1_lvl2s6380/run.log`
- `scratch/agent/m6/g1_lvl2s6380long/run.log`
- matching `keys.log` and `mc_ctl.txt` files

Use `grep -c` and `grep -n ... | head/tail` only; do not print a whole log.
Build a compact table for route markers, `keys.log`, `mc_ctl.txt`, `origin=`,
`phase=`, task markers, `[spike-st]`, `fd57=`, and `[spike-vu8]`. Establish
whether s6380 reached the same phase/origin/task route as s6378.

Competing hypotheses:

- H-recipe: forced route/input differs; route, phase, origin, task, or key
  markers differ.
- H-timing: route matches but the wedge fell outside the captured interval;
  route markers match and FD57 is absent in both s6380 witnesses.
- H-instrument: the target store witness or ring filter missed FD57; FD57 is
  present in `[spike-st]` without a corresponding `[spike-vu8]` row.

DISCRIMINATING MEASUREMENT: route identity plus FD57 presence in both witness
streams. If a mismatch exists, correct only the smallest recipe difference and
run one capture with the existing build. If the route matches and FD57 appears,
replay the post-vd clamp. If it matches and FD57 remains absent, select timing;
if only `[spike-st]` has FD57, select instrumentation.
