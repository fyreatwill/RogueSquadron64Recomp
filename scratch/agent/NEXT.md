# NEXT (s5676): fold s5675_g1fly_{a,b}
Fold SOAK-RESULTS lines for s5675_g1fly_a/b (logs scratch/agent/m6/s5675_g1fly_*/run.log). Compare: [pad-host] edges (is 'a' = fire?), objective/kill counters ([objbool]/[cco]), end-screen via scratch/agent/m6/fb_brightness.py, crash/stall lines.
Outcomes: a advances counters vs b -> H-g1, extend to a steered kill route toward mission win; identical -> H-g2, design a state-aware autopilot (read target positions from RDRAM) or move to G3; no 'a' edges -> H-g3 fix key map. If results absent, check the queue (soak_queue/running).
HYPOTHESIS-ID: g1-mission-progression
