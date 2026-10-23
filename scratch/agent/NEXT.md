# NEXT: fold g1_lvl5_tele4 ([objsnap] first run), then lvl6 ctl+tele pair

HYPOTHESIS-ID: g1-mission-coverage-sweep

Fold: grep -c '\[objsnap\]' scratch/agent/m6/g1_lvl5tele/run.log and `zsh tools/g1_d_compare.sh 5`. Control: TELE>0. If objsnap prints id=N changes under TELE, (d) has a counter for lvl5 (compare to ctl, which needs the same build: requeue g1_lvl5_ctl as ctl3). If zero objsnap lines with HUDBIT on, the counter array is not moved via these accessors on lvl5 -> read docs/M6-OBJECTIVE-COUNTER-WRITERS.md for the real end-gate. Then queue lvl6 ctl+tele (diff recipes first).
