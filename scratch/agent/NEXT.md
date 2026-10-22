# NEXT: G1 - s5873: fold s5872_hold600_god / _ctl soak verdicts (queued s5872)
Hypotheses: (a) death is health (god+revive => mission passes vi 15987, no a0=1), (b) non-health kill (still a0=1 with [god-dead] revives firing), (c) godmode doesn't see health in this mission (no [god-dead] dead=1 lines = no positive control, result void).
Read: scratch/agent/SOAK-RESULTS.md tail, the two logs: grep -a 'god-dead\|m47\|endMissionCleanup'. If (b): add lives byte 0x80130B10+[0x8010C9E8] + PLPOS to [m47] via tools/apply_s5847_mask_log.py and regen.
HYPOTHESIS-ID: g1-mission-progression
