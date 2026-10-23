# NEXT: fold g1_lvl8 pair, then queue lvl9 pair

HYPOTHESIS-ID: g1-mission-coverage-sweep

Fold: `grep '\[objsnap\]' scratch/agent/m6/g1_lvl8{ctl,tele}/run.log | awk '{print $2}' | sort | uniq -c`; look for ids beyond the baseline id=1 cycle with tele hits >0 (lvl5/lvl7 show id=2 moving).
Then queue lvl9 pair (sed LEVEL=9 from g1_lvl8_*.sh). lvl6 (d) still unshown: widen objsnap array via level-table objective slot.
