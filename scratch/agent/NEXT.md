# NEXT (s5679): fold s5678_g1fly_{a,b} (harness fixed: AP_OVERRIDE now precedes COMMON)
Control first: run.log must contain "[autopilot] armed: N events" and [pad-host] lines (grep -a). If absent, harness still broken - fix before anything else.
Then compare a (fire+steer) vs b (steer only): [pad-host] a=1 edges, mission-state/objbool counters, fb_brightness (python3 scratch/agent/m6/fb_brightness.py <tag>), crash/stall lines.
Outcomes: a advances counters vs b -> H-g1, extend steered kill route toward win; identical -> H-g2, state-aware autopilot (RDRAM target positions) or G3; no 'a' edges with armed autopilot -> H-g3 fix key map.
HYPOTHESIS-ID: g1-mission-progression
