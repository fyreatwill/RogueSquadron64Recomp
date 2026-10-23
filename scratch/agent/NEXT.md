# NEXT: fold g1_lvl7_tele, then lvl8 pair

HYPOTHESIS-ID: g1-mission-coverage-sweep

Fold: `grep '\[objsnap\]' scratch/agent/m6/g1_lvl7tele/run.log | awk '{print $2}' | sort | uniq -c` vs ctl (only id=1 0<->4 cycle, baseline). Any other id, with `tele=` >0, = lvl7 (d) passes.
lvl6 finding: tele=9, no objsnap lines in tele or ctl -> (d) not shown via objsnap; consider reading the lvl6 level-table objective slot to widen the snapshot array.
Then queue lvl8 pair (copy g1_lvl7_*.sh, LEVEL=8), then lvl9.
