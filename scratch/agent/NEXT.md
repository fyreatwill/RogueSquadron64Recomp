# NEXT: fold g1_lvl4_tele5 (objsnap on lvl4), then queue lvl6 ctl+tele pair

HYPOTHESIS-ID: g1-mission-coverage-sweep

lvl5 result: forced hits move only objsnap id=2 (fail counter). Fold: grep objsnap scratch/agent/m6/g1_lvl4tele/run.log (expect an id with 2->3 if the s5949 objcount move is real; none => s5949 reading was noise). Then queue g1_lvl6_ctl/tele (copy g1_lvl5 recipes with LEVEL=6; tele needs ROGUESQ_TELE_BOLT=1).
