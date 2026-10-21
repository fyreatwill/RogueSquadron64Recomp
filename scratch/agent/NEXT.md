# NEXT: find the non-health exit trigger (H-OTHER selected, s5733)
Evidence: s5732_g3a revived health yet mission origin still alternated 0x620400<->0x690400 (6 dead events), same as log-only arm b.
Work unit: add a write-watch (env-gated) on the mission exit/results-state word in the godmode block of src/main/main.cpp; print writer PC/caller + value at each change, plus a revive counter. Positive control: watch fires on every write to the word (and on the known mission-win probe ROGUESQ_MISSION_WIN). Run one soak with GODMODE3=1.
Outcomes: writer is fail-timer/objective code -> mission has a non-health fail condition (name it); writer is teardown driven by input/autopilot -> autopilot artifact.
HYPOTHESIS-ID: g1-gameover-cause
