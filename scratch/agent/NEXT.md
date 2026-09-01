# NEXT work unit — M5 LLE-off spin-yield discriminator

HYPOTHESIS-ID: m5-real-audio-route-pivot

Session 3504 disabled forced LLE and avoided the prior crash, but stopped at
VI 640 before title. The next unit must test one new route arm before selector
rows are interpreted.

Competing hypotheses and discriminating measurement:

- `H-SpinYieldDependency`: with LLE off and spin-yield off, the run reaches
  title, showing the 640 advance depends on the yield arm.
- `H-LLEOffAdvanceBlocker`: the changed arm remains at VI 640, showing the
  pre-title blocker survives both route changes.
- `H-AudioRouteAlternateFailure`: a new crash or distinct pre-title failure
  appears and becomes the next route discriminator.
- `H-AudioRouteInstrumentation`: the startup control or phase is absent,
  proving the capture setup is invalid rather than the route being blocked.

Discriminating measurement: run one bounded real-image retry with
`ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_LLE_FORCE=0`, and
`ROGUESQ_SPIN_YIELD=0`, while keeping the same startup, phase, dispatch,
audio-return, and selector controls. A 1024 title transition selects
`H-SpinYieldDependency`; continued VI 640 selects `H-LLEOffAdvanceBlocker`; a
new crash selects `H-AudioRouteAlternateFailure`; missing startup/phase
controls select `H-AudioRouteInstrumentation`. The independent retail control
remains a required preflight, not a substitute for port title reachability.

Run from `build/`, make the route change explicit in the command, capture to a
non-dot final path under `scratch/agent/`, and SIGKILL any watchdog survivor.
Do not interpret a pre-title selector null as a table-writer result.
