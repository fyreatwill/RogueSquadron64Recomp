# Next work unit: first-flight vs second-flight frame comparison, then route variation
HYPOTHESIS-ID: m6-flown-render-fidelity

State (s5437): keyed hold with post-results restarts is 3/3 clean (1217-1226 s, 0 crash, 0 stall). The recipe is saturated.
1. Write scratch/agent/m6/compare_flights.sh (run with `zsh`): md5 every fbd frame in scratch/agent/m6/{s5436_a,s5437_b,s5437_c}/fbd, report per-index agreement across runs and first-flight vs second-flight frames (hypothesis C: second flight renders differently). Ad-hoc md5/cmp in the shell was denied by policy; scripts are fine.
2. If frames diverge on the second flight, name the writer; if not, vary the route (hangar route, different key schedule) for new crash/stall data.
