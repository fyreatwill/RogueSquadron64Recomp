# NEXT: G1(d) decode the objective-table target for the moving counters (lvl7 id=2, lvl8 id=6, lvl5 id=2)
HYPOTHESIS-ID: g1-d-objective-gate
s5994: counters move under TELE and reset to 0 (peak 3 / 4); target unknown.
Hypotheses: H1 reset-to-0 = objective completed/cleared (target = peak); H2 reset = counter is a transient/hit-window not a goal count; H3 target is higher than the 10 forced hits reached.
Work unit: find the code reading the snapshotted array (base 0x80138060) in a completion compare (grep recompiled funcs for 0x80138060 / objective-count loads), read the target value for lvl7/lvl8 from the level table, compare to peak. H1 => (d) PASS; H3 => queue a longer tele soak.
Use: python3 tools/objsnap_summary.py scratch/agent/m6/g1_lvl*tele/run.log
No aim/steer work.
