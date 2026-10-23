# NEXT: G1(d) static: who issues requestMissionTransitionMode a0=2/3 (success) and what gates it?
HYPOTHESIS-ID: g1-d-objective-gate
s5996: lvl7 end = 3rd death (a0=1), lvl8 end = a0=2 ph=7 requests in both arms. Counters never gate an observed end.
Hypotheses: H1 a0=2/3 callers gated by objective counters/flags (then TELE could finish a level); H2 gated by timer/scripted trigger (lvl8 ph=7 requests start with no hits); H3 gated by enemy-count/DL-chunk check.
Work unit (offline, no game run): grep generated funcs for callers of requestMissionTransitionMode (0x800FB190) with a0=2 or 3 (see docs/M6-PHASE-MACHINE.md, M6-S5747-FAIL-ARM-CENSUS.md), list each caller's gating condition, decide whether objective counters (0x8013805C+4n) feed it. Record verdict; if H1 holds, define a (d) PASS test on lvl8; if H2/H3, close (d) as PARTIAL-final and move to G4/G3. No aim/steer work.
