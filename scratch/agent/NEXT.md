# Next work unit: confirm log caps on var_d/e, then vary the route
HYPOTHESIS-ID: m6-flown-render-fidelity

s5441 capped [tricnt]/[rt64drawn] (4000 lines/phase). Read SOAK-RESULTS.md tail (m6_keyed_var_d/e) and `ls -la scratch/agent/m6/s5441_var_*/run.log`.
- run.log well under ~200 MB and summary present with crashlines=0 vi_stalls30s=0: cap confirmed; queue hangar-route-variation and 1200 s-with-variation soaks (needs a recipe edit; runs are capped at 600 s by the loop, so long holds need a different launcher).
- Still huge: `tail -c 200000000 run.log | cut -c1-24 | sort | uniq -c | sort -rn | head` and cap the new dominant prefix.
- Any CRASH/stall: backtrace (ASan arm in a separate build dir; lldb is unusable here), name writer, root-cause fix.
