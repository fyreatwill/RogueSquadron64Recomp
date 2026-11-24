# NEXT (s7877)
HYPOTHESIS-ID: g3-det-render-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State: 6 missions are render-exact on every det-tick flight frame (b17, m12, m6 0x31=5, m11 0x31=10, m3 0x31=2, m8 0x31=7; s7876).
tools/s7868_det_frame_cmp.py now gives a flight verdict on its own: flight runs from the last port phase to the post-flight
blank, rc 0 means flight is exact, rc 1 means a flight diff, and pre-flight and post-flight diffs are reported but do not set rc.
Unit: a 7th mission, 0x31=3 (mission 4, Liberation of Gerrard V, the G5a crash mission; on a forced route it is the most
valuable mission still unchecked):
`env RBIN=1 zsh tools/s7849_det_pair.sh 3 scratch/s7877/v3` (screen unlocked; ~16-25 min), then
`python3 tools/s7868_det_frame_cmp.py scratch/s7877/v3/r1/retail.bin scratch/s7877/v3/p1.bin --plant --neg scratch/s7877/v3/p2.bin`.
Outcomes: rc 0 with plant PASS and neg PASS -> 7 missions, then 0x31=0 (mission 1). rc 1 -> a real flight render defect on a
det tick: localise it with tools/s7869_island_probe.py. If p1 is not H-exact (state fork), report the fork tick and score
only the exact prefix. If the cut line says MISMATCH, check the blank by hand (scratch/s7875/blanks.py). Delete the bins after.
Parked: g3-cinematic-half-frame-phase (s7874 table; island A absent in m3 and m8).
