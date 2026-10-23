# NEXT: fold g1_lvl6t pair ([objsnap-t] ctl vs tele)

HYPOTHESIS-ID: g1-mission-coverage-sweep

Fold: `grep -h '\[objsnap-t\]' scratch/agent/m6/g1_lvl6{ctl,tele}/run.log | awk '{print $2,$3}' | sort | uniq -c` per arm; confirm TELE positive control fired and 0 crash/stall. Tele-only ids = lvl6 (d) responds. Then summarize (d) across lvls 1-9 and move to G3 render fidelity.
