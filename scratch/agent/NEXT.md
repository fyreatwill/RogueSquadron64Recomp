# NEXT work unit — M5 LLE-on no-spin discriminator

HYPOTHESIS-ID: m5-real-audio-route-pivot

Session 3505 kept forced LLE disabled and also disabled spin-yield. It still
stopped at VI 640 with live controls and no crash, selecting the LLE-off
advance blocker. The next unit must test one new route arm before selector
rows are interpreted.

Competing hypotheses and discriminating measurement:

- `H-SpinYieldDependency`: with LLE restored and spin-yield still off, the run
  reaches title, showing spin-yield is the missing advance aid.
- `H-NoSpinAdvanceBlocker`: the LLE-on/no-spin arm remains at VI 640, showing
  the blocker is broader than the LLE-off route.
- `H-AudioRouteAlternateFailure`: a new crash or distinct pre-title failure
  appears and becomes the next route discriminator.
- `H-AudioRouteInstrumentation`: the startup control or phase is absent,
  proving the capture setup is invalid rather than the route being blocked.

Discriminating measurement: run one bounded real-image retry with
`ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_LLE_FORCE=1`, and
`ROGUESQ_SPIN_YIELD=0`, while keeping the same startup, phase, dispatch,
audio-return, and selector controls. A 1024 title transition selects
`H-SpinYieldDependency`; continued VI 640 selects `H-NoSpinAdvanceBlocker`; a
new crash selects `H-AudioRouteAlternateFailure`; missing startup/phase
controls select `H-AudioRouteInstrumentation`. The independent retail control
remains a required preflight, not a substitute for port title reachability.

Run `scratch/agent/s3505_lle_off_no_spin_real_audio.sh` as the template, change
only `ROGUESQ_LLE_FORCE=1`, capture to a non-dot final path under
`scratch/agent/`, and SIGKILL any watchdog survivor.
Do not interpret a pre-title selector null as a table-writer result.
