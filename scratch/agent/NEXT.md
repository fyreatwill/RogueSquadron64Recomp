# NEXT work unit — M5 silent LLE-on no-spin discriminator

HYPOTHESIS-ID: m5-real-audio-route-pivot

Session 3506 restored forced LLE while keeping spin-yield disabled. It still
stopped at VI 640 with live controls and no crash, selecting the broader
no-spin advance blocker. The next unit must test whether that blocker depends
on real audio before selector rows are interpreted.

Competing hypotheses and discriminating measurement:

- `H-RealAudioDependency`: silent LLE-on/no-spin reaches title, showing the
  VI-640 blocker depends on real-audio work.
- `H-AudioIndependentNoSpinBlocker`: silent LLE-on/no-spin remains at VI 640,
  showing the blocker is independent of the audio route.
- `H-SilentLLERouteFailure`: a new crash or distinct pre-title failure appears
  and becomes the next route discriminator.
- `H-AudioRouteInstrumentation`: the startup control or phase is absent,
  proving the capture setup is invalid rather than the route being blocked.

Discriminating measurement: run one bounded silent retry with
`ROGUESQ_AUDIO_UCODE=0`, `ROGUESQ_LLE_FORCE=1`, and `ROGUESQ_SPIN_YIELD=0`,
while keeping the same startup, phase, dispatch, audio-return, and selector
controls. A 1024 title transition selects `H-RealAudioDependency`; continued
VI 640 selects `H-AudioIndependentNoSpinBlocker`; a new crash selects
`H-SilentLLERouteFailure`; missing startup/phase controls select
`H-AudioRouteInstrumentation`. The independent retail control remains a
required preflight, not a substitute for port title reachability.

Run `scratch/agent/s3505_lle_off_no_spin_real_audio.sh` as the template, change
only `ROGUESQ_AUDIO_UCODE=0`, capture to a non-dot final path under
`scratch/agent/`, and SIGKILL any watchdog survivor.
Do not interpret a pre-title selector null as a table-writer result.
