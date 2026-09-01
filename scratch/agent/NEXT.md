# NEXT work unit — M5 real-audio route qualification

HYPOTHESIS-ID: m5-real-audio-route-qualification

Session 3502 could not run the selector comparison: two real-image retries
crashed before title at `spTaskSchedulerThread+9556`, guest PC `0x8000834C`.
The next unit must qualify the real-audio route before selector rows are
interpreted.

Competing hypotheses and discriminating measurement:

- `H-AudioRouteStable`: a corrected real-image retry reaches title; title
  controls and selector rows become available.
- `H-AudioRouteCrash`: the same pre-title scheduler crash recurs; selector
  comparison remains unevaluable and the route blocker is reproducible.
- `H-AudioRouteInstrumentation`: controls or phase are absent without the
  known crash; the route recipe or capture setup is invalid and must be fixed.
- `H-AudioRouteAlternateFailure`: a different pre-title crash appears; the
  failure family, not selector state, becomes the next discriminator.

Discriminating measurement: run one bounded real-image/LLE/spin-yield retry
with the existing dispatch, phase, and audio-return controls plus the selector
pre-call witness. A 1024 title transition and selector control/rows select
`H-AudioRouteStable`; the exact `0x8000834C` crash with live startup control
selects `H-AudioRouteCrash`; missing controls select
`H-AudioRouteInstrumentation`; another crash selects
`H-AudioRouteAlternateFailure`. The independent retail control remains a
required preflight, not a substitute for port title reachability.

Run from `build/`, use the validated real-image/LLE/spin-yield/autopilot
environment from Session 3502, capture to a non-dot final path under
`scratch/agent/`, and SIGKILL any watchdog survivor. Do not interpret a
pre-title selector null as a table-writer result.
