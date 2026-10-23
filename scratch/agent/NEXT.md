# NEXT: fold lvl5 ctl2/tele2 pair, then g1_d_compare.sh 5

HYPOTHESIS-ID: g1-mission-coverage-sweep

S5951: lvl5 NSW A/B folded: nsw att1 pass (mission t=79); nonsw att1 nomission (viewer stall origin 0x62BD00, s3294-stall lines) then att2 pass. So the viewer stall is FLAKY (intermittent), not caused by NO_SAVE_WRITE. Re-queued g1_lvl5_ctl2 / g1_lvl5_tele2 (same recipe, retry pair).
Fold: read m6/g1_lvl5{ctl,tele}/keys.log (same tags). If both reach mission, run g1_d_compare.sh 5 and fold (d). If nomission again, capture lldb backtrace of the 0x62BD00 viewer stall (M6 rule: root-cause, no guard). Then lvl6+ (d).
