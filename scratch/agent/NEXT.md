Single next work unit (s5634): fold s5633_force{0,2}_{a,b} soaks from SOAK-RESULTS.md. Control: logs must show [objdraw] ... forced=1 used=0/2 and [objbool] ids 1 / 3 respectively.
Hypothesis R: fail arm needs bool[1]==1 && bool[7]==1. Prediction: force0 (id 1) reproduces the 0x64 fail arm deterministically (bool 7 set path still needed - grep setObjectiveBoolean 7 setters offline); force2 (id 3) never fails.
If force0 never fails either, R is refuted -> look at what sets bool 7.
HYPOTHESIS-ID: m6-mission-endurance
