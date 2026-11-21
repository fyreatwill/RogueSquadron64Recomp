# NEXT (s7757)
HYPOTHESIS-ID: rdp-output-gate-219-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner report, then new SOAK-RESULTS lines.
s7756 put the hangar H-state visibility property in the sweep (tools/s7756_hstate_gate.py --controls, GREEN 2/2, CAP=2048 ctl
RED). Both RDP-output gates (s7753 byte-exact, s7756 visibility) cover only dd1 4:3 and 16:9 dd2: the owner's 21:9 recipe
(ROGUESQ_ASPECT=21:9, dd4, FPS60, STANDINS=1) has retained snaps only for L1 dd8 flight (scratch/s7751), none for the hangar,
cutscene or attract at 21:9.
Unit (one game run, owner-recipe-shaped, screen unlocked): tools/s7754_capture_route.zsh at ASPECT=21:9 dd4 FPS60 STANDINS=1
with ROGUESQ_S7751_EVERY spread over attract / SELECT GAME / hangar / L4 cutscene / L4 flight (retain 1 snap per phase, hangar
as a _end pair). Then add the non-hangar snaps to s7753 SNAPS (cap=1048576 tg=1 capc=2048) and the hangar pair to s7756 PAIRS;
rerun both with --controls and the full sweep (--jobs 2).
Hypotheses: H-exact (21:9 non-hangar tasks replay byte-exact, hangar pair invisible: same as 16:9) / H-wide-drift (a 21:9-only
path - FARMAX, wide scissor, stand-ins DL - is not snapshot-replayable or renders visibly live-vs-end) -> discriminator: the
s7753 EQUAL/DIFF per snap and s7756 live-end ge2LSB on the 21:9 pair, with the existing ctls.
Max 2 CPU-heavy jobs.
