# NEXT: fold s6537 cap_40 and cap_inf, then pick a cap
HYPOTHESIS-ID: g1c-span-reject-predicate
Folded so far (s6538): cap0 57.9 ms/task, 18.7 tasks/s, tight frac 0.0285; cap120 87.2 ms, 17.9 tasks/s, frac 0.0735 (p90 0.26). Pending: s6537_cap_40 and s6537_cap_inf in scratch/agent/soak_queue (loop runs them). If SOAK-RESULTS lacks them, check queue; do not babysit.
Work unit: per arm dir scratch/agent/m6/g1_lvl1s6537_{40,inf}: g1b mean (awk over [g1b] lines; restrict to flight seconds if possible) + `python3 -I tools/g1c_fixed_score.py <dir>/fbd 4500`.
Outcomes: inf must reproduce ~127 ms / 10.5 tasks/s (positive control; else the cap wrapper changed behaviour). If frac(40)/frac(120)/frac(inf) saturate early while cost scales -> choose that cap as dd>1 default; if linear -> expose knob, send owner contact sheet of cap 0/120/inf.
