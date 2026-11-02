# NEXT: G3e residual dd4 terrain dip (every ~481 VI) — name it, fix it
HYPOTHESIS-ID: g3e-dd-terrain-dropout

Done s6788: dropouts were the 120-cell span-bypass cap making dd>1 terrain bistable; the dd>1 bundle now sets
BYPASS_MAXCELLS=-1 + UCODE_CAP=1048576. Default-path lvl1 FPS60: dd3 0 in-flight drops (was 90), dd4 6 (was 47).
Residual at dd4 only: every ~481 VI (the autopilot 8 s a/sl/a/sr cycle) the stream's kept-cell count decays
~2200 -> ~850 over 4-5 frames, then jumps back in one frame; window (site 2) constant, ucode cap 0 fires.
First: fold the queued soaks s6788_g3e_lvl5_dd4 / lvl10_dd4 (SOAK-RESULTS.md; census in scratch/s6788/soak_census_lvl*.txt,
`python3 scratch/s6788/census_drops.py <file>`).
Unit (one build, one run): extend tools/apply_s6788_ddtrace.py site 4 with the per-call reject reasons inside
streamTerrainGridCellsByDistance: far-clip d2 >= *0x8009DEB4 (s6418 farclip), pool-cap exhaustion (node alloc NULL /
count == cap 8192), and min/max d2 of kept; plus craft pitch/roll/yaw from guest RAM at site 1. Run
`env ARMS="v4" zsh scratch/s6788/arms.zsh` (rename the arm) and join with scratch/s6788/join.py around the dips.
Hypotheses: H-farclip (the dd-scaled far clip / d2 cutoff moves with pitch and trims far cells during the turn),
H-pool (node pool exhausted in the densest swaps, nearest-first walk drops the far tail), H-retail (same dip at dd1
in the same phase — check dd1 trace kept series at the same VI phase). Outcome: the reason counter that rises on dip
frames names the limit; fix it in the bundle and re-run dd4 to 0 in-flight drops.
Then: G2b (Chapter II crawl audio chop, ITERATION 3c).
