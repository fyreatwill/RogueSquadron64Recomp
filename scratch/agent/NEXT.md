# NEXT (s5677): fold s5676_g1fly_{a,b}
s5675 arms were void (AP never reached game; fixed in m6_god_common.sh via AP_OVERRIDE, s5676). Fold SOAK-RESULTS lines for s5676_g1fly_a/b (logs scratch/agent/m6/s5676_g1fly_*/run.log, keys.log).
Control first: keys.log has `mission t=` (else harness still broken - check ROGUESQ_AUTOPILOT in the process env). Then compare [pad-host] edges ('a' = fire?), [objbool]/[cco] counters, end screen (scratch/agent/m6/fb_brightness.py), crash/stall lines.
Outcomes: a advances counters vs b -> H-g1, extend to steered kill route toward win; identical -> H-g2, state-aware autopilot (read target positions from RDRAM) or G3; no 'a' edges -> H-g3 fix key map.
HYPOTHESIS-ID: g1-mission-progression
