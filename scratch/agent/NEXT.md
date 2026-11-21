# NEXT (s7761)
HYPOTHESIS-ID: rdp-output-gate-select-level
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner report, then new SOAK-RESULTS lines.
s7760 closed PAUSE / ABORT LEVEL / MISSION FAILED (24/24 exact, s7753 GREEN 20/20). The last owner-visible screens not scored at the
owner 21:9 recipe: SELECT LEVEL (only matched vs angrylion at 4:3 dd1, s6785) and LEVEL DESCRIPTION. They are reached by the forced
level-select route (tools/s7754_capture_route.zsh default: FORCE_SAVE_MISSION/FORCE_UNLOCK=4, AP starts at 6..41 s).
Unit (one game, screen unlocked, host idle): `env EVERY=60:24:<from> SECS=120 zsh tools/s7754_capture_route.zsh w219_select
ROGUESQ_ASPECT=21:9 ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_FPS60=1 ROGUESQ_STANDINS=1` with <from> chosen from the s7757 w219 route sheet
(scratch/s7754/w219/sheet.jpg + its run.log autopilot fs= lines: pick the fs just before the SELECT LEVEL screen). Attribute snaps to
screens by BOTH the window sheet and the autopilot-fire/dump interleave in run.log (s7760 method). Then
`python3 tools/s7757_route_replay.py scratch/s7754/w219_select/snap`; per DIFF `python3 tools/s7755_hstate_visibility.py <snap> --cap 1048576 --tg 1`.
Hypotheses: H-exact (add 1-2 snaps to s7753 SNAPS + bump the sweep regex) / H-state (add a pair to s7756 PAIRS, name the RAM region:
SELECT LEVEL draws a 3D planet/map, like the hangar craft DL) / H-race (live-end ge2LSB > 0: name the writer).
After this, RDP-output coverage is complete: do NOT add more coverage units; take an owner report or ITERATION 3c rung.
Max 2 CPU-heavy jobs.
