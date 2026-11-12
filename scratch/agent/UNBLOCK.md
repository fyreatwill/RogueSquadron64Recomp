# UNBLOCK s7179
Route: 1 (refute) -> 2 (fix locally). The block said "out of turns / unit too large". It was neither.
Observation that proved it false: the iteration-67 transcript shows `echo WORKING > scratch/agent/STATUS` at 02:24:20Z, then a
blocking wait, then a kill at 02:32:32Z = +480 s (DONE_GRACE) + one 15 s poll. runner.sh's watchdog treated any STATUS newer than
ITER_START_MARK as "finished", WORKING included. Both retries died within 15 s because STATUS was already stale.
Fix: tools/agent/runner.sh watchdog now also requires STATUS to read DONE or BLOCKED.
Verification (sandbox, fake claude sleeping 50 s, DONE_GRACE=10): old runner + WORKING killed at 21 s (reproduces the bug);
new runner + WORKING runs the full 50 s; new runner + DONE still killed at 20 s (positive control, so the hang guard is intact).
Also: sum_L*r.txt is always empty, so NEXT.md now says to wait on pgrep instead. The L17 capture is on disk and NEXT.md resumes from it.
