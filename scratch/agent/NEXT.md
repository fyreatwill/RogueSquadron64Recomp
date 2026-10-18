# Next work unit: find when/why the unflown mission fails and measure flight-time endurance
HYPOTHESIS-ID: m6-flown-render-fidelity

State (s5429): terrain relief renders in free flight (dune seen VI 3000-9000). Mission shows MISSION FAILED by VI 12000, so the 600 s hold is ~half flight, half results screen (and the fb hash 'distinct' count is inflated by it).
Hypotheses: (A) failure is ship destroyed/crashed into terrain with no input; (B) timer/objective failure; (C) autopilot key fires a fail/retry path.
Discriminator: `FBD_EVERY=10` run, 300 s hold, find first fb frame showing the failure text (scan dumps with tools/ppm2png.py), view the 5 frames before it (explosion/ground vs HUD timer) and grep the run.log around that VI for phase changes. Positive control: the results frame already seen at VI 12000.
Then: add flight keys (l/r/su/sd) so the ship survives, hold >=10 min of real flight.
