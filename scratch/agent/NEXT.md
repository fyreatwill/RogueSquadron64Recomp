# NEXT: fold G1(d) lvl4/5 pairs, then explain applyDat drop under TELE

HYPOTHESIS-ID: g1-mission-coverage-sweep

S5948: lvl1-3 folded: TELE fires, BooleanCount writes rise, [objcount] val= absent for lvl2/3, applyDat falls under TELE (lvl2 114->42, lvl3 44->20).
Next unit: when g1_lvl{4,5}_{ctl,tele} land in SOAK-RESULTS.md, run `zsh tools/g1_d_compare.sh 4` and `5`, fold.
Then: phase-gate applyDat counts per VI phase (same-run) to test whether the drop is run-length vs real suppression (H: TELE kills triggers vs H: shorter window).
Discriminator: applyDat per-phase counts in tele vs ctl arms.
