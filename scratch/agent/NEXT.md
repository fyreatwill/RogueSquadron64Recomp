# Next work unit: read m6_mission_v2_{a,b,c} verdicts; root-cause first distinct crash/stall
HYPOTHESIS-ID: m6-mission-endurance

Enqueued s5409 (fixed recipe: mission origin 0x690400 in either format counts as route success).
Read: tail SOAK-RESULTS.md; scratch/agent/soak_results/m6_mission_v2_*/keys.log (+ crash_excerpt.txt).
Clean summary => check onset vs key activity (attract vs real mission). CRASH => backtrace (main.cpp ~10078), name writer, root-cause fix, two-arm. STALL => VI origin + log rows. SCREEN-LOCKED => re-enqueue.
