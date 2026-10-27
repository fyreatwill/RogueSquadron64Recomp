# NEXT: RESUME — deterministic FD57 capture-route audit
HYPOTHESIS-ID: g3c-owner-visual-b

Checkpoint resume only. Do not rerun s6380 or rebuild before completing the
offline audit. The existing artifacts are:

- `scratch/agent/m6/g1_lvl2s6380/run.log`
- `scratch/agent/m6/g1_lvl2s6380long/run.log`
- matching `keys.log` and `mc_ctl.txt` files
- positive-control reference: `scratch/agent/m6/g1_lvl2s6378/run.log`

Work unit: use bounded `grep -c`/`grep -n` and a compact table to compare
the two s6380 logs with s6378 for route markers, `keys.log`, `mc_ctl.txt`,
`origin=`, `phase=`, task markers, `[spike-st]`, `fd57=`, and
`[spike-vu8]`. Do not cat a large log. The comparison must establish whether
the runs reached the same phase/origin/task route before interpreting the
missing FD57 row.

Competing hypotheses and discriminator:

- H-recipe: the forced route/input differs; predicted by a route, phase,
  origin, or task mismatch.
- H-timing: the same route ran but the wedge occurred outside the captured
  interval; predicted by matching route markers with no FD57 in either
  witness.
- H-instrument: the target store witness or ring filter missed an FD57 event;
  predicted by FD57 in `[spike-st]` without a corresponding `[spike-vu8]` row.

DISCRIMINATING MEASUREMENT: same phase/origin/task route as s6378, then FD57
presence in `[spike-st]` and `[spike-vu8]`. If the audit finds a route/input
mismatch, make only the smallest recipe correction and run one deterministic
capture with the already-built instrument. If the route matches and FD57
appears, replay the post-vd clamp. If the route matches and FD57 remains
absent, select H-timing; if only `[spike-st]` has FD57, select H-instrument.
