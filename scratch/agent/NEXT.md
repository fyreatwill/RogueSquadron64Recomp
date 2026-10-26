# Next: fold s6290 retail + wide G3c arms (queued; the loop runs them)
HYPOTHESIS-ID: g3c-owner-visual
[g3c] lines are in scratch/agent/m6/g1_lvl1s6290_g3c_<arm>/run.log (NOT soak_results/). Run `python3 -I tools/g3c_jerk.py <run.log>` per arm.
Already folded (s6291): fps60 alt 0.625, both alt 0.632, spacing 97% 1-VI. Need retail (control) and wide.
Outcomes: retail alt ~0.5 and fps60/both ~0.63 -> H-fps60 selected (camera cadence); retail ~0.62 -> H-retail, FPS60 refuted; wide-only high -> H-aspect.
If retail/wide are not done yet, do (a) terrain-edge arm table (retail vs dd2/dd3 vs ASPECT, fb dumps) offline-first, then (b) spikes reference check.
