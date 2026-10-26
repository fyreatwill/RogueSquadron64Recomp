# Fold s6270 lvl18 + s6271 plume-loop verdicts, then pick the next unclosed rung
HYPOTHESIS-ID: m6-endurance-patched-build
Read s6270_patched_l18 and s6271_plume_title16_patched lines in SOAK-RESULTS.md (plume summary: scratch/agent/soak_results/s6271_plume_lldb_title16_patched/summary; titles=N/16 bad=0 is clean). Any STOP/BREADCRUMB -> read run<r>.lldb backtrace, name writer, root-cause fix. If clean, next rung: a concrete game bug needing a C patch (add target to tools/weaken_patched_funcs.py PATCH_WEAKEN, two-arm qualify as s6269) or owner-reported issues.
