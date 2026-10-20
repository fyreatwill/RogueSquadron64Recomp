# NEXT (s5675): close G2 or move to G1
Facts (s5674): speech-window AI PCM is rail-free, band-limited (<3 kHz), ~11x control level; WAVs in scratch/agent/m6/s5674_raw/wav/. Intelligibility needs a human ear.
Hypotheses: H-f1 speech audible -> G2 closed; H-f2 only music/SFX audible (speech masked/ducked) -> solo the voice slot pre-mix; H-f3 fuzz residual -> compare retail oracle hf_ratio (already matched s5671).
Unit: rung G1 (mission progression from real input): write a soak recipe that reaches mission 2 from real input after mission 1 win (no ROGUESQ_MISSION_WIN poke), log crashes/stalls. Keep ROGUESQ_PCM_RAW armed in soaks (cheap) so a listen is always possible.
HYPOTHESIS-ID: g1-mission-progression
