# NEXT: G1 — fold the s5786 hudbit4 dump soaks (who/what triggers setHudEnableBit4 ~190 s into the mission?)

Soaks `s5786_hudb_althold` and `s5786_hudb_noalt` (queued s5786) log `[hudbit4]` (ra/gate/flagword), `[hudbit4dump]` (nonzero objective bools 1..0x70 + timers 0..7) and host backtraces for the first 4 calls. Logs: scratch/agent/soak_results/s5786_*.log (verdicts in SOAK-RESULTS.md).
- H-script-fail: dump at the call preceding `[mtm] a0=2` shows a specific objective bool newly set (compare with the previous dump) -> name it via the objective-bool table, trace its setter.
- H-timer: a timer value at/over a limit at that call -> timer idx + limit.
- H-ours: noalt arm calls setHudEnableBit4 too (or the althold arm does it with no bool/timer change) -> look at autopilot input at that time (btn 0x8000 at t~379/385).
Controls: dump lines exist; a nonzero bool appears in some line. If setHudEnableBit4 is never reached in either arm, the run did not reproduce (s5784 reproduced once) — check `[livesbyte] 3->2` presence first and re-queue.
If the host backtrace only shows recomp host frames with no script info, read the caller's guest args (a0..a3) by extending the same patch.
HYPOTHESIS-ID: g1-mission-progression
