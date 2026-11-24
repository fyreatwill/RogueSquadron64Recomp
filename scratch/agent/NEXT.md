# NEXT (s7876)
HYPOTHESIS-ID: g3-det-render-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State: 5 missions render-exact on every det tick (b17, m12, m6 0x31=5, m11 0x31=10, m3 0x31=2, s7875). Caveat (s7875): the s7868
scorer's final phase runs past the last mission tick into the end-of-mission screen (animation-phase diffs, not state); bound
flight by the post-flight tri-less blank.
Unit (one bounded change + one run): teach tools/s7868_det_frame_cmp.py to cut the final phase at the first >=3-frame tri-less run
after the exact-run start (report "flight" and "post-flight" separately; rc 1 only for flight interior diffs), with a control
(a plant inside flight still caught; the s7875 bins re-captured or a new mission). Then a 6th mission:
`env RBIN=1 zsh tools/s7849_det_pair.sh 7 scratch/s7876/v7` (mission 8; screen unlocked; ~16 min), score with --plant --neg.
Outcomes: flight 100% exact -> 6 missions, keep sweeping; a non-exact flight frame on a det tick -> real render defect, localise
with tools/s7869_island_probe.py. Delete bins after.
Parked: g3-cinematic-half-frame-phase (s7874 table; island A absent in m3).
