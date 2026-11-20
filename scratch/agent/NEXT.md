# NEXT (s7691)
HYPOTHESIS-ID: g6c-owner-sheet-s7690

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
s7690 fixed STANDINS=frame mode (ROGUESQ_S7690_PARITY, default on): half the stand-ins were never re-tested by the game's
two-frame view-test slice, so every frame-mode proof/sheet before s7690 (s7628, s7688) under-reported stand-ins.
Work unit: refresh the G6c owner proof + sheet on the fixed binary, same recipe as s7688 (scratch/s7688_standins_proof.sh:
L1 dd2, L1 dd4, L4 dd2, L4 dd4, STANDINS=frame HOLD 150), plus ROGUESQ_S7690_PARITY=0 as an in-run control arm on ONE of
them (L4 dd4) so the gain is shown same-binary on a second level.
Expected: window-1 flicker px/triplet and early items rise vs s7688 (465/638/856/2488) on every arm; window-2 off controls
unchanged (~44/104/154/207); synthetic control PASS. If an arm does NOT rise, its stand-ins were all in the tested group by
luck: check [s7690-par] fix counts (tools/s7690_par_tally.py) before calling it.
Then: replace the OWNER-OPT-INS sheet pointer with the refreshed cluster sheet. Default STANDINS stays off; owner judges.
One game at a time, SIGKILL only, <=2 CPU-heavy jobs, screen unlocked.
