# NEXT: fold g1_lvl5_tele3, then g1_d_compare.sh 5 (ctl arm = m6/g1_lvl5ctl from ctl2)

HYPOTHESIS-ID: g1-mission-coverage-sweep

S5952: lvl5 ctl2 reached mission (t=80s, hold 303s, 0 crash/stall). tele2 reached mission too but had NO ROGUESQ_TELE_BOLT export (recipe defect; TELE=0 over 834 tally lines) so compare 5 is void on the tele side. Requeued g1_lvl5_tele3 with the export.
Fold: after tele3 runs, `zsh tools/g1_d_compare.sh 5`; positive control = TELE>0 in the tele arm. Then queue lvl6 ctl+tele pair (copy g1_lvl4_tele recipe incl. the export; ALWAYS diff tele vs ctl recipe before queueing). Then lvl7+.
