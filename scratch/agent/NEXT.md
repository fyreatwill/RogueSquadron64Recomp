# NEXT: G1 - s5874: fold s5873_hold600_god / _ctl soak verdicts (queued s5873)
Hypotheses: (a) death is health (god+revive => mission passes vi 15987, no a0=1), (b) non-health kill (still a0=1 with [god-dead] revives firing), (c) godmode doesn't see health (no [god-dead] dead=1 lines = no positive control, result void).
Read: SOAK-RESULTS.md tail; scratch/agent/m6/s5873_hold600_god/{summary,run.log}: grep -a 'god-dead\|m47\|endMissionCleanup\|requestMissionTransitionMode'. If summary says allattempts-failed, read fail_att*.log CRASH pc-symbol first (check it is not the diagnostic again).
If (b): add lives byte 0x80130B10+[0x8010C9E8] + PLPOS to [m47] via tools/apply_s5847_mask_log.py and regen.
HYPOTHESIS-ID: g1-mission-progression
