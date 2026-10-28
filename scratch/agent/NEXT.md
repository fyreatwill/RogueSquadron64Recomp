# NEXT: same-run alternating-cap toggle for the g1c span-reject cap
HYPOTHESIS-ID: g1c-span-reject-predicate
State (s6541): cross-run cap arms (s6537-s6540) are noise; 3 same-recipe runs gave tight 0.029-0.031, 56-68 ms/task. Cap effect unproven.
Work unit: in apply_s6537_bypasscap.py add env ROGUESQ_CAP_ALT=<N> that alternates cap 0 / 120 / inf every N swaps (log cap in force per swap), rebuild once, run ONE lvl1 recipe (copy s6540_explicit120.sh), then bin sd_wall and terrain fraction by cap-in-force with tools/g1c_fold.py (add --by-cap) and the fbd frames tagged by cap.
Outcomes: per-cap ms/task differ >20% and tight fraction differs -> cap real, pick by cost; no difference within same run -> cap irrelevant at lvl1, leave cap120 and proceed to dd3/dd4 holds lvl 1/5/10. Positive control: cap0 vs inf must show differing reject counts in the log.
