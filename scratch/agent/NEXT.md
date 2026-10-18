# Next work unit: what condition in runInMissionFrame (funcs_42.c ~12256) passes a0=2 to requestMissionTransitionMode?
Hypotheses: H1 objectives-complete (success); H2 death/lives==0; H3 timer/scripted event. Discriminator: static read of generated runInMissionFrame around the call, then rerun m6_bp_trans.sh s5472a with extra reads of lives/objective words at the requestMissionTransitionMode bp. s5471a showed a0=2 and phase 0->4 (PORTING-STATE s5469). Control: watch on 0x3470 must hit.
HYPOTHESIS-ID: m6-mission-end-trigger
