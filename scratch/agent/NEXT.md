# Next work unit: consume s5036_guard34_force_control verdict
HYPOTHESIS-ID: heap-guard-need-census
Read SOAK-RESULTS.md line for s5036 (keys1.log in scratch/agent/soak_results/s5036_guard34_force_control/). guard3>0 && guard4>0 && coalesce_next>0 && crash=0 => all heap-guard zeros on the mission route are two-source (r1: no site); record in CURRENT-TRUTH and close the census. guard3 or guard4 == 0 => force wiring broken (check grep "guard3_force" in built funcs), fix before reading anything.
After that: pivot to an M3 idiom-class audit (priority 3) with a committed guard, or the renaming sweep per CLAUDE-loop priority 4 rules. Rebuild with scratch/agent/s5034_build.sh.
