# Fold s6272 plume attach verdict (patched build), then pick the next unclosed rung
HYPOTHESIS-ID: m6-endurance-patched-build
Read the s6272_plume_attach16_patched line in SOAK-RESULTS.md and scratch/agent/soak_results/s6272_attach_patched/summary. Require control=PASS (injected SIGSEGV caught) else it is a tooling null. titles=N/16 bad=0 with control PASS is clean. Any STOP/BREADCRUMB -> read run<r>.lldb backtrace, name writer, root-cause fix. If clean, next rung: a concrete game bug needing a C patch (add target to tools/weaken_patched_funcs.py PATCH_WEAKEN, two-arm qualify as s6269) or G3 render fidelity.
(s6271 was a broken recipe — no data; see PORTING-STATE s6272.)
