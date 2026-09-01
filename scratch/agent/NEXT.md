# NEXT work unit — M5 route pivot after repeated real-audio crash

HYPOTHESIS-ID: m5-real-audio-route-pivot

Sessions 3502–3503 both failed before title at
`spTaskSchedulerThread+9556`, guest PC `0x8000834C`, so the unchanged recipe
must not be repeated. The next unit must test one new route arm before selector
rows are interpreted.

Competing hypotheses and discriminating measurement:

- `H-AudioRouteConfig`: a single changed audio/LLE route arm reaches title,
  showing the prior crash is configuration-sensitive.
- `H-AudioRouteCrash`: the changed arm still crashes at `0x8000834C`, showing
  the blocker survives that route change.
- `H-AudioRouteAlternateFailure`: a different pre-title failure appears and
  becomes the next route discriminator.
- `H-AudioRouteInstrumentation`: the startup control or phase is absent,
  proving the capture setup is invalid rather than the route being blocked.

Discriminating measurement: run one bounded real-image retry with one explicit
route change from the failed `AUDIO_UCODE=1`/LLE/spin-yield arm, while keeping
the same startup, phase, dispatch, audio-return, and selector controls. Title
and selector controls select `H-AudioRouteConfig`; the same
`0x8000834C` crash selects `H-AudioRouteCrash`; another crash selects
`H-AudioRouteAlternateFailure`; missing startup/phase controls select
`H-AudioRouteInstrumentation`. The independent retail control remains a
required preflight, not a substitute for port title reachability.

Run from `build/`, make the route change explicit in the command, capture to a
non-dot final path under `scratch/agent/`, and SIGKILL any watchdog survivor.
Do not interpret a pre-title selector null as a table-writer result.
