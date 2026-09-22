# Next work unit: identify the audio-pump route boundary

HYPOTHESIS-ID: m5-audio-pump-route-boundary

S3695 showed that the existing qualified real-audio arm can stall at the
initial 320 VI before the M5 RSP/source controls, while the independent retail
control reaches hangar and observes its writer PCs. The predecessor join is
unevaluable; do not interpret absent target rows as a DMEM producer result.

Competing route hypotheses:

- `H-AudioPumpGate`: a required audio-pump gate prevents the real arm leaving
  boot 320.
- `H-LLERouteStall`: the selected LLE/audio route stalls before target VI due
  to its task or yield configuration.
- `H-PhaseInstrumentBlind`: the port reaches progress but the phase/control
  callbacks are not live; this must be rejected by an independent VI control.

Discriminator: one same-run table containing the port's RSP source positive
control, VI 1024 and 512 transitions, DMEM source control, and source-range
writer rows. A live RSP control followed by no VI transition selects a route
stall; VI transitions with no M5 controls selects instrument blindness; all
controls live reopens the DMEM predecessor unit.

Use the existing binary from `build/` and batch the route arms in one run/build
where possible. Keep the independent VI/phase logger and RSP positive control
enabled. Start by comparing the current real-audio/LLE recipe against the
known silent/Broke route or the smallest audio-pump gate toggle; do not add a
DMEM join field.

Require the discriminator table above. If the route stalls before 1024 again,
inspect the existing audio-pump gate/task boundary; if it reaches 1024/512,
resume the predecessor join without changing its fields.
