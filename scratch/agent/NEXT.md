# NEXT: RESUME — deterministic FD57 capture-route audit
HYPOTHESIS-ID: g3c-owner-visual-b

This is a checkpoint resume. Do not rerun s6380 or rebuild before the offline
audit. The existing s6380 artifacts are the two lvl2 logs and their route
metadata; the known positive-control reference is
`scratch/agent/m6/g1_lvl2s6378/run.log`.

Work unit: compare those runs with bounded `grep -c`/`grep -n` and a small
table containing tag, summary/exit status, VI-origin transitions, phase,
`[spike-st]` count, FD57 count, and `[spike-vu8]` count. Locate the s6380 log
paths from the prior session entry or its build/run artifacts; do not cat a
large log. Compare `keys.log`, `mc_ctl.txt`, `origin=`, `phase=`, and task
markers. If the route/phase/origin differs from s6378, make the smallest input
or recipe correction and run one deterministic capture with the already-built
instrument. If it reaches the same route and FD57 appears with `[spike-vu8]`,
interpret the post-vd clamp replay. If it reaches the same route with no FD57,
select H-recipe/H-timing. If `[spike-st]` has FD57 but no ring block, select
H-instrument. Do not interpret a new null without the route and generic-ring
positive controls firing.

Hypotheses: H-recipe (the forced route exits or changes phase), H-timing (the
wedge occurs later), H-instrument (the store witness/ring filters it).
DISCRIMINATING MEASUREMENT: same phase/origin/task route as s6378, then FD57
presence in `[spike-st]` and `[spike-vu8]`.
