# NEXT: fold s6540_default_r2 + s6540_explicit120 (queued) and resolve H-wrapper vs H-noise
HYPOTHESIS-ID: g1c-span-reject-predicate
State (s6540): cap120 is the built dd>1 default, but the default-path run (63 ms/task, tight 0.031) looked like cap0, not the explicit cap120 arm (87 ms, 0.074).
Work unit: read SOAK-RESULTS for s6540_default_r2 and s6540_explicit120; fold with `python3 tools/g1c_fold.py scratch/agent/m6/g1_lvl1s6540_{defr2,exp120}` and `python3 tools/g1c_fixed_score.py <dir>/fbd 4500`.
Outcomes: explicit120 ~87 ms/0.27 and both defaults ~60 ms/0.03 -> H-wrapper: diff the getenv path in s6537_take (is the cap actually applied when unset? log used/rejected counts per swap). All three scatter -> H-noise: retract s6539 ordering, build a same-run toggle (cap alternated per swap/VI-phase) instead of cross-run arms. Then proceed to dd3/dd4 holds lvl 1/5/10 only after the default is trusted.
