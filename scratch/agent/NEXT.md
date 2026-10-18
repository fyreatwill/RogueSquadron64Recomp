# Next work unit: read m6_mission_v3_{a,b,c} verdicts (first run with a PASSING detector control)
HYPOTHESIS-ID: m6-mission-endurance

s5412: v3 a/b previously died at 0s (control sequence ended at t=36; fixed to 39). Check keys.log first line says 'detector-control OK'.
Do: read SOAK-RESULTS + soak_results/m6_mission_v3_*/keys.log (summary: last_vi, origins, stalls). If stalls>0 or CRASH: backtrace (lldb/ASan), name writer, root-cause fix. If clean: lengthen hold / confirm flight scene, escalate to second mission transition.
