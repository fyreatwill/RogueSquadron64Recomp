# NEXT: G1c per-cell cost — streamTerrainGridCellsByDistance, the largest single per-cell term
HYPOTHESIS-ID: g1c-dd-headroom
Context (s7021, per-frame xctrace split of the dd6 tog3 cap toggle 8192 -> 10240 cells, L1 21:9 WIDEWIN owner path): gfx thread +1.72 ms/frame
(spread: ucode self 0.70 over 7 blocks, DPC submit 0.68), game thread +0.91 ms/frame of which streamTerrainGridCellsByDistance +0.31 (base 0.64
ms/frame, +48% for +25% cells), renderFlatMeshFaceGroup +0.15, processGridCellByDistance +0.08. e9prov counters already gated (s7021).
G5i: fixed, owner look only — check CURRENT-TRUTH item 1 first.
Source: /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c (RECOMP_FUNC void streamTerrainGridCellsByDistance);
existing patches on it: tools/apply_s6493_stream_cum.py (exit/skip counters [streamcum]), tools/apply_s6883_spancell.py.
Hypotheses: H-fullwalk (it scans every window cell each frame to rank by distance, O(cells) even when nothing changes -> cache the ranked
list or skip unchanged cells), H-superlinear (+48% for +25% cells: a sort/insertion that is O(n log n) or O(n^2) in queued cells),
H-retail-work (each cell's stream/mesh work is genuine and must be done: only host-side speedups like -O3 / inlining help).
Discriminator, ONE run, offline-first: (1) read the function (disassembly via the s7014 xctrace_fn_lines.py line split on the C7 trace in
scratch/s7021/tp2.xml, thread '[Game] MAIN', obj = the funcs_9 .o) to find which loop lines carry the +0.31; (2) if a loop is per-cell
per frame with no change detection, count calls / iterations per frame at caps 8192 vs 10240 with one counter set (tog3, same run).
Iterations ratio ~1.25 -> H-fullwalk (linear); ~1.5+ -> H-superlinear. Then one change with a same-run tog A/B (xor8 split, shift control).
