# Next work unit: fold stick/fire variation soak verdicts
HYPOTHESIS-ID: m6-flown-render-fidelity

s5439 queued m6_keyed_var_{a,b,c} (scratch/agent/m6_keyed_hold_var.sh). Read SOAK-RESULTS.md tail and scratch/agent/m6/s5439_var_*/summary.
- Any CRASH/stall: lldb/ASan backtrace, name writer, root-cause fix.
- All clean 3/3: input variation is saturated too; next vary mission (different hangar selection) or longer 1200 s holds with variation.
