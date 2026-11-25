# NEXT (s7915; s7914 was the gate-contract fix, this unit did not run)
HYPOTHESIS-ID: g3-m6-island-b-nondet
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, docs/OWNER-REVIEW-QUEUE.md answers,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7913): ROGUESQ_DET_CLOCK=1 (VI-keyed) left the s7912 particle element nondeterministic (C1 vs C2 0/212), but the clock
streams themselves diverged at record 0 (first osGetTime VI 28 vs 20), so H-clock is untested. DET_CLOCK=2 (65104 ticks per call
per thread, no VI term) and a host-RA CLOCKLOG (atos-symbolisable, control PASS s7913/ractl) are built.
Hypotheses: H-clock (element consumes osGetTime), H-race (host thread vs game thread on the element buffer), H-uninit.
Discriminator, 2 arms, same recipe as scratch/s7913/run.sh with ROGUESQ_DET_CLOCK=2 (copy the script, change the env and dirs):
1. Score element: tools/s7912_elem_cross.py 635A40/f0/s3/w1 FFFFFFFFFE793C D1=.. D2=.. C1=scratch/s7913/m6c1/p1.bin
2. Clock streams: tools/s7913_clocklog.py D1/clock.bin --cmp D2/clock.bin. Per-thread streams in mode 2 can still interleave
   differently in the file, so compare values per RA (game-thread RAs getTimeSinceLastFrame/recordFrameTimestamp/getTimeLow32).
Outcomes: game-thread clock values equal AND element exact -> H-clock; values equal AND element differs -> H-clock refuted (then
XTRACE_MEM write watch on the element vertex source, H-race/H-uninit); values differ -> DET_CLOCK=2 not deterministic either: record,
stop the clock thread (budget: this is iteration 2 of 2) and take the next ladder rung (owner queue / G1e).
If DET_CLOCK=2 breaks the mission (time never advancing real-time waits), record it, same budget rule.
