# Next work unit: confirm log-flood fix on var_c, then vary the mission
HYPOTHESIS-ID: m6-flown-render-fidelity

s5440 capped the [s4234-ENTRY] probe. Read SOAK-RESULTS.md tail (m6_keyed_var_c) and `ls -la scratch/agent/m6/s5439_var_c/run.log`.
- run.log << 1 GB and summary present: flood fix confirmed; then queue 3 soaks varying hangar selection / 1200 s holds with variation.
- Still huge: grep the dominant line prefix in run.log (`cut -c1-20 | sort | uniq -c | sort -rn | head`) and cap that source.
- Any CRASH/stall: lldb/ASan backtrace, name writer, root-cause fix.
