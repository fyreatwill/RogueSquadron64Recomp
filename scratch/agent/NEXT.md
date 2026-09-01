# NEXT work unit — re-qualify silent route for selector-load capture

HYPOTHESIS-ID: m5-task-field-writer

Session 3490 added the selector-load witness, but the port arm did not reach
the title phase, so the selector discriminator is not evaluable.

Competing hypotheses and discriminating outcomes:

- `H-SilentRouteNondeterminism`: the silent route occasionally stalls in 640;
  a retry reaches title and fires both controls.
- `H-RecipeMismatch`: the capture recipe differs materially from Session 3488;
  restoring its exact environment reaches title and fires both controls.
- `H-BuildRegression`: the newly linked generated call changes the route;
  a probe-off same-binary arm reaches 640 while the probe-on arm does not.

Discriminating measurement: run the same binary with the selector-load probe
enabled, requiring the title transition and both
`m5-selector-load-control` and `m5-selector-writer-control` markers. If title
is reached and controls fire, proceed to the planned load/source join. If an
exact-recipe retry reaches title, select `H-RecipeMismatch`; if a probe-off
same-binary arm also stalls at 640, select `H-SilentRouteNondeterminism` or
`H-BuildRegression` only after that route-specific comparison.

Exact command: `zsh scratch/agent/run_s3490_m5_upstream_selector.sh` after
restoring the Session 3488 environment; keep the SIGKILL watchdog and run from
`build/`. Do not build another selector instrument until title controls fire.
