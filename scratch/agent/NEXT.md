# NEXT: fold g1_lvl6_tele, g1_lvl7_ctl, g1_lvl7_tele

HYPOTHESIS-ID: g1-mission-coverage-sweep

Fold: `grep '\[objsnap\]' scratch/agent/m6/g1_lvl{6tele,7ctl,7tele}/run.log | awk '{print $2}' | sort | uniq -c`.
Controls: tele runs need TELE>0, ctl runs TELE=0. An id appearing in tele but not ctl = lvl objective slot (d passes). lvl4 note: ctl5 also shows id=15/id=5, so lvl4 (d) is NOT shown.
Then queue lvl8 pair (copy g1_lvl7_*.sh, LEVEL=8), then lvl9.
