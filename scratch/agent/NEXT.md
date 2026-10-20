Single next work unit (s5624): STOP the hudbit4 chain (5 sessions, no discriminator). Pivot to G1: explain why the per-run objective-boolean ids differ by 1 (0x2/0xC/0x6F/0x16 vs 0x1/0xB/0x6E/0x15) and why only 8 calls occur in 420 s.
Step 1 (offline, cheap): grep lv2 / setObjectiveBoolean callers in RecompiledFuncs for how id is computed (a0 = base + a per-run index?); name the per-run source (RNG seed? mission-select index? uninitialised memory?). A per-run value changing a script id is itself a determinism defect candidate.
Step 2: extend apply_s5622_objbool_log.py to log ALL calls with VI frame number and the caller function name (use the generated-function call-site tag, not r31), and 1 mission-time stamp; soak x2 as s5624_objbool_{j,k}.
Outcomes: id source = uninitialised/RNG => fix root cause, re-soak; id source = mission index => benign, move on to why script stalls at 8 calls (compare to retail oracle ordering if reachable).
HYPOTHESIS-ID: m6-mission-endurance
