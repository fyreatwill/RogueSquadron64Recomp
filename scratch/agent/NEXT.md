# Next work unit: read m6_mission_v3_c + m6_mission_v4_{a,b,c} verdicts
HYPOTHESIS-ID: m6-mission-endurance

s5413: v3_a/b clean with controlled detector. v4 adds ROGUESQ_FB_HASH + `fbhash maxrun= distinct= total=` line in soak_results/m6_mission_v4_*/keys.log (control line "fbrun-control OK" must be present).
Do: read SOAK-RESULTS + keys.log. Outcomes: crash/stall -> backtrace (ASan arm in separate build dir; lldb unusable), name writer, root-cause fix. distinct~1 / huge maxrun -> frozen frame with live VI: find who writes the fb. Clean + animating -> design second-mission transition (route beyond mission onset) or composite holds.
