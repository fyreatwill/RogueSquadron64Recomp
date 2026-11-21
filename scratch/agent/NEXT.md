# NEXT (s7758)
HYPOTHESIS-ID: rdp-output-gate-standins-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner report, then new SOAK-RESULTS lines.
s7757 put the owner's 21:9 recipe in both RDP-output gates (s7753 13/13 byte-exact, s7756 3/3 hangar pairs). Gap left: the
21:9 flight snaps are L4, where stand-ins add few objects. Stand-in display lists are built by HOST code (src/main/rs64_standins.cpp)
into guest RAM 0x81700000..0x81800000 and threaded into the game's visibility bucket; if the host rewrites them while the gfx task
reads them, those tasks are H-state like the hangar (not begin-snapshot replayable), and possibly visible.
Unit (one game run, screen unlocked, host idle): LV=10 (stand-ins add 192/280 on L10, s7749)
`env LV=10 EVERY=250:24 SECS=230 zsh tools/s7754_capture_route.zsh w219_L10 ROGUESQ_ASPECT=21:9 ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_FPS60=1 ROGUESQ_STANDINS=1`
then `python3 tools/s7757_route_replay.py scratch/s7754/w219_L10/snap` (begin/end/b==e per task); grep `[standins-spawn]` t=
against snap vi to know which flight snaps had stand-ins added. Same run control: a ROGUESQ_STANDINS=0 run is NOT same-run; use
instead the per-task begin-vs-end replay (b==e False marks H-state) and the hangar tasks in the same run as the positive control.
Hypotheses: H-exact (L10 flight tasks with stand-ins replay byte-exact from begin and end: add 1-2 snaps to s7753 SNAPS) /
H-standins-state (flight tasks DIFF with begin != end and the influential pages sit in 0x81700000+: run s7755 visibility on the
pair; visible -> a real stand-ins race to fix in rs64_standins.cpp (double-buffer the DL), invisible -> add to s7756 PAIRS).
Max 2 CPU-heavy jobs.
