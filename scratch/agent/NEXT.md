# NEXT (s5680): state-aware autopilot for G1
Open-loop steering crashes into terrain (s5679). Build: find ship position/pitch/altitude in RDRAM (use godmode health addr neighbourhood; oracle if needed), log them at 1 Hz in a flown-mission soak with positive control (value must change with stick input), then close the loop in the autopilot (level pitch, fire at targets). Commit tool change.
Discriminating outcome: pitch/alt field tracks stick -> closed-loop feasible; not found -> try G2 audio noise comparison (title music oracle vs port AI PCM).
HYPOTHESIS-ID: g1-mission-progression
