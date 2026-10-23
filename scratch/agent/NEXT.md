# NEXT: G1(d) lvl7/lvl8 — identify which objective counter id moves under TELE and whether an end gate responds
HYPOTHESIS-ID: g1-d-objective-gate
s5993 closed the lvl1 ground thread (H1 legit). Folded (d): lvl7 tele objsnap 33 vs ctl 2; lvl8 objcount 0->4.
Work unit: run `python3 tools/apply_s5953_objsnap.py` (or grep '[objsnap]' in scratch/agent/m6/g1_lvl{7,8}{ctl,tele}/run.log) to list the ids/values that move; compare to the level's objective table; decide whether forced hits reach a completion/fail counter.
Outcomes: a counter reaches its target => (d) PASS for that level, record; moves but short of target => queue a longer tele soak; no ids move => (d) not met, root-cause the applyDat path.
Do NOT do aim/steer work (out of scope).
