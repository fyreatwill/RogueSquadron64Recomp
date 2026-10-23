# NEXT: fold lvl5 NO_SAVE_WRITE A/B, then rerun lvl5 ctl/tele pair

HYPOTHESIS-ID: g1-mission-coverage-sweep

S5950: lvl5 ctl/tele pair was void (viewer 0x62BD00 never exits; nomission x3). Queued g1_lvl5_nsw (NO_SAVE_WRITE on) vs g1_lvl5_nonsw (off).
Fold: read m6/g1_lvl5{nsw,nonsw}/keys.log. nonsw mission + nsw nomission => H1 (flag blocks viewer exit; find which save write lvl5 needs, or drop the flag for lvl5 and re-queue ctl/tele with NSW_ENV=). Both fail => regression/flaky (diff vs s5715 build). Both pass => flaky; rerun pair.
Then: g1_d_compare.sh 5, fold; continue lvl6+ (d).
