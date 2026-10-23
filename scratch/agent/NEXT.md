# NEXT: fold g1_lvl4_ctl5, g1_lvl6_ctl, g1_lvl6_tele

HYPOTHESIS-ID: g1-mission-coverage-sweep

Fold: `grep objsnap scratch/agent/m6/g1_lvl{4ctl,6ctl,6tele}/run.log | awk '{print $2}' | sort | uniq -c`.
lvl4: if ctl5 also shows id=15 0-3 cycling => baseline, forced hits move nothing on lvl4 (H-null). If ctl has none => id=15 is forced-hit driven.
lvl6: tele TELE>0 and ctl TELE=0 are required controls; look for any id besides 15. Then queue lvl7 pair.
