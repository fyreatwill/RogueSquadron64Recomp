# NEXT: G1 - s5875: find what sets requestMissionTransitionMode a0=1 when health is held at 150
Hypotheses: (a) lives byte hits 0 (non-health death), (b) a0=1 is a scripted/timer mission end (e.g. objective fail or time), (c) a different player-HP field than the one godmode revives.
Measure: add lives byte 0x80130B10+[0x8010C9E8], caller ra (use bt from rs5846_log) and mission timer to [m47] via tools/apply_s5847_mask_log.py, regen, run god+ctl hold600 as queued soaks. Outcome splits: lives drop to 0 => (a); ra points at timer/objective fn => (b); neither => (c).
HYPOTHESIS-ID: g1-mission-progression
