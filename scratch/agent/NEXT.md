# NEXT: fold s5732_g3a (tight-thread revive) / s5732_g3b (log-only control)
Read SOAK-RESULTS.md tail; per arm grep run logs (scratch/agent/m6/s5732_g3{a,b}/run.log) for `[god3]` and mission_cycles.
H-LATE: a has mission_cycles 0 and flight > 541 s with revives > 0 -> latch is health-death; next: make revive part of a real-input pass/G1 progress.
H-OTHER: a still cycles -> second fail condition; log the results-state writer at the dead transition.
Control: b prints [god3] lines with history (damage shape); a prints them too and revives.
HYPOTHESIS-ID: g1-gameover-cause
