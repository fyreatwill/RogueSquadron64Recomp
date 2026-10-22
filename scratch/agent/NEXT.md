# NEXT: G1 - s5871: who calls endMissionCleanup at ~VI 15987 in the hold600 mission?
Hypotheses: (a) player death / ship destroyed (b) mission-win/timer condition (c) leftover harness key (START or hold) re-entering pause/quit.
Discriminator: rerun s5869 recipe (AP_HOLD=600) WITHOUT ROGUESQ_LOG_HUDBIT (avoids the diagnostic fault) plus a log on the mainGameLoop caller of endMissionCleanup (gMissionState/exit-reason globals) and PLPOS hp near the end; compare to keys.log timing. Check grep 'endMissionCleanup\|beginMissionEndTransition\|player.*dead' in run.log and position/hp trace before VI 15987.
Queue it as scratch/agent/soak_queue/s5871_endreq.sh (copy of the s5869 script, HUDBIT removed from COMMON via env override).
HYPOTHESIS-ID: g1-mission-progression
