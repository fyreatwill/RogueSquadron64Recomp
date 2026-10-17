# Next: in-mission input response (playability beyond the passive 300 s hold)
HYPOTHESIS-ID: m6-mission-input
Hypotheses (why in-mission input might not work on the port):
 H1 input reaches the game (osContGetReadData pad bits change in mission) and the mission reacts; port is playable.
 H2 keys reach SDL but mission-phase pad polling is stubbed/stale (pad struct constant under keys).
 H3 pad reaches game but a mission-phase crash/stall triggers once the player ship receives non-zero stick/fire (crash>0 or VI stops).
Discriminator: reuse scratch/agent/s4958_after_6a2900.sh keyed route to mission (onset ~t=181 s); then hold a key (winctl key) for 5 s, vs. a no-key control window in the SAME run (phase-gated on mission origin 0x690400/0x620400). Log pad bytes returned by the cont wrapper (existing AI/cont census hooks) + DL/VI counts + crash for key window vs control window. Positive control: hangar keys already change origin (s4956).
Fallback if mission cannot be reached (s5046 regression): record and fix keyed title->hangar first.
