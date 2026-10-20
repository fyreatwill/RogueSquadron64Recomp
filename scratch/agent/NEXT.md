Single next work unit (s5621): fold s5620_nopoke_{d,e,f,g} from SOAK-RESULTS.md.
Method: for each, grep -n '\[hudbit\|\[cco\]\|mission-win\] flagword' scratch/agent/m6/s5620_nopoke_X/run.log. In any run with a [hudbit4] line, read the [cco] lvN line(s) directly preceding it (ra is always 0).
Outcomes: [cco] lvN just before hudbit4 => level N's checkComplexObjectives sets it, find which objective condition (static read of that function); no [cco] before => script stub hookSetHudEnableBit4 caller; 0/4 hudbit again => natural gate-4 needs a different trigger, grep writers of 0x8010C9E0 flagword directly (watch on write, not on setter).
If zero hits in 4, do NOT queue more: statically read lv2_checkComplexObjectives to see what sets bit 4.
HYPOTHESIS-ID: m6-mission-endurance
