Route 3 — re-scoped the dependency after routes 1 and 2 did not satisfy the
full port-side census.

Route 1 refutation attempt: read `tools/oracle/README.md`, the oracle
`--help`, and its source. The installed debugger-off core API has a second
route, `--vi-poll`, that does not depend on debugger callbacks. I added the
small `--status-poll` option to poll the 18 status-table words through the same
core API. In the phase-gated run
`scratch/agent/s2012-oracle-status-poll.log`, the oracle reached VI 1024 at
17.3s and hangar VI 512 at `0x006AB400`/`0x006AB800` at 38.4s. In that same
run slot 0 at `0x154620` changed `0x00 → 0x01 → 0x02 → 0x03 → 0x00` at
43.1s, 43.4s, and 48.8s. This disproves the narrower claim that the retail
status transition needs the missing generated tree. The exact debugger-on
writer watch was also tried with the whole-RDRAM positive control; it reached
VI 640 only, so it cannot replace the port-side writer/thread census.

Route 2 local satisfaction attempt: searched the workspace and the maintained
N64Recomp checkout for complete generated bundles. The local batch4–batch8
archives and the s389/s390 snapshots contain the 45 generated files and the
three companion artifacts, but predate the s2007/s2008 status instrumentation;
none is a phase-valid s2007 tree. No unreachable git object supplied one. The
four modified companion symbol files remain a human authorization boundary.

The next unit in `scratch/agent/NEXT.md` is therefore the blocker-free retail
status-value control. The open dependency is recorded in
`docs/CURRENT-TRUTH.md`: a phase-valid generated tree or owner authorization is
still required only for the port-side writer/thread attribution join.
