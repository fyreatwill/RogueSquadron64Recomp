# NEXT: fold g1_lvl5_ctl3 (objsnap id=2 baseline?) then lvl4 tele rerun with objsnap

HYPOTHESIS-ID: g1-mission-coverage-sweep

tele4: only [objsnap] id=2 0->1 (fail counter). Discriminator: ctl3 same build. grep objsnap scratch/agent/m6/g1_lvl5ctl/run.log. ctl shows id=2 change => H-null (forced hits move no counter); ctl shows none => H-fail. Then requeue g1_lvl4_tele to learn which id gave 2->3 there.
