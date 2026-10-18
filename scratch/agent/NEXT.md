# Next work unit: read m6_mission_v3_{a,b,c} verdicts (first valid stall detector)
HYPOTHESIS-ID: m6-mission-endurance

s5411: detector now counts '[vi] update_screen' rows with a synthetic positive control; v2 'no stall' results are unproven.
Do: read SOAK-RESULTS + keys.log (summary has last_vi, origins). If any stalls=N>0 or CRASH: backtrace (lldb/ASan), name writer, root-cause fix. If all clean: lengthen hold / inspect origins to confirm flight scene, then escalate to second mission transition.
