# Fold s6270 patched-build soak verdicts, then pick the next unclosed rung
HYPOTHESIS-ID: m6-endurance-patched-build
Read the three s6270_patched_l{11,14,18} lines in SOAK-RESULTS.md. rc=0 -> note clean in ledger. Any crash/stall -> lldb backtrace, name the writer, root-cause fix. If all clean, take the next open ladder rung (G3 hangar artifacts, or a concrete game bug needing a C patch: add the function to tools/weaken_patched_funcs.py PATCH_WEAKEN and qualify two-arm like s6269).
