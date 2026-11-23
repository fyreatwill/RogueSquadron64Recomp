# NEXT (s7870)
HYPOTHESIS-ID: g3-det-prefix-render
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7869): det-exact ticks = per-frame render oracle; b17 1120/1120 and m12 5662/5662 flight frames exact vs retail.
m12's only non-exact island (143 frames) is pre-flight (port phase 6 / retail 640-wide, before tick 0), state-driven
(tools/s7869_island_probe.py: p1 and p2 wrong by different values on the same frames).
Unit (cheap, offline, one tool change): make tools/s7868_det_frame_cmp.py print the port phase ordinal / retail VI width of
every map segment (frames() already returns it as fr[i][1]), so islands are placed vs flight without a side script; then
re-score the RETAINED s7844 (0x31=5) pair (scratch/s7868/s7844_cmp.txt names its paths) and place its "before" tri-geom
diffs and "after" tri-count fork in phase terms.
Outcomes: H-preflight = all s7844 pre-run diffs in the pre-flight phase (same class as m12) -> G3 det render line closes with
3 missions; H-flight = non-exact frames inside flight BEFORE the s7844 state fork tick -> real render candidate, print the
differing tris and find the DL op.
If s7844 bins are gone, pick an exact mission from the s7862 sweep table instead (one det pair, RBIN=1, ~25 min) and delete
its bins after scoring.
