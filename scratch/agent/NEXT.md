# NEXT: fold g1_lvl9 pair

HYPOTHESIS-ID: g1-mission-coverage-sweep

Fold: `grep '\[objsnap\]' scratch/agent/m6/g1_lvl9{ctl,tele}/run.log | awk '{print $2}' | sort | uniq -c`; check CRASH/stall. Then lvl6 (d) (widen objsnap array via level-table objective slot), then (c) framebuffer captures for all levels.
