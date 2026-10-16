# Next work unit: consume s5033 heap-guard census verdict
HYPOTHESIS-ID: heap-guard-need-census
Read the s5033_heap_guard_census line in scratch/agent/SOAK-RESULTS.md (keys1.log in soak_results/s5033_heap_guard_census/).
Outcomes: mission_onset_t>=0 and guard2/3/4/coalesce/r1 all 0 -> patch moot (single-source, no fire control); fold into CURRENT-TRUTH, withdraw toolchain dependency as non-load-bearing. Any >0 -> the guarded original path yields bad pointers: name the writer (iron rule 11), escalate toolchain need. mission_onset_t=-1 -> route failed, rerun once.
If a fire control is wanted: add a fixup env that forces one bad r3 in alloc-tail-guard2 (tools/fixup_*.py), rebuild, rerun.
