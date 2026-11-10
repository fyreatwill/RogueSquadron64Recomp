# NEXT: FPS60 near-wall flicker: what the mesh/emit stage makes of the near cells across an episode
HYPOTHESIS-ID: fps60-wall-mesh-emit
Context (s7104): streamTerrainGridCellsByDistance keeps the eye cell and forward rows (K) on every call of all 8 episodes; S/C/N culls never fire,
and the empty-footprint rate near the eye is the same as in flight. So the wall cell is in the distance-sorted list. s7098 showed the wall is absent
from the game's RDP stream. The loss sits between the list and the RDP: buildGridCellMeshForFace (called from buildVisibleTerrainGridAroundCamera,
s6417 meshlog anchor after_11 0x80043AAC; LOD dist^2 tiers 0x8009DE94..A0, far cutoff DEB4), per-face/vertex emission, or the F5 ucode clip.
Unit (one build, one run: scratch/s7099/arm.zsh 6 4 s7105a "ROGUESQ_G1E_LIMIT=1 ROGUESQ_G1E_WIN=600 ROGUESQ_G3C_LOG=1
  ROGUESQ_S7101_CHASE=$PWD/scratch/s7105/push_a.txt ROGUESQ_S7104_CELL=1 ROGUESQ_S7105_EMIT=1" 120 240):
 1. Static read buildGridCellMeshForFace first: per-cell paths that emit nothing (back-face test, LOD tier, vertex-cache/DL chunk overflow, a
    per-face near/behind test).
 2. New tools/apply_s7105_emit.py: for every list node within ring<=3 of the eye cell (node +0xC col, +0x10 row, +8 dist^2), log per frame:
    LOD tier chosen, faces tested / emitted, vertices/tris written to the DL. Append to the same cc line stream (key m, frame).
 3. Same run, per frame: RDP tri count (existing G5B/G3C counters) so emitted-vs-drawn can be compared.
 Positive control: far cells must show the lower LOD tiers and fewer tris than ring 0 (the tier test visibly fires).
Hypotheses:
 H-emit-skip  the wall cell's faces are skipped by the mesh stage (back-face/near test with the eye on the wrong side) -> emitted tris for the
              near ring drop at the episode while the cell stays K
 H-lodswap    the tier for the eye-ring cell flips across a dist^2 boundary at 60 fps, and the other tier's mesh has no wall faces
 H-clip       tris are emitted as in flight, but the RDP tri count drops -> F5 ucode near-plane clip/cull (camera inside the near distance)
 H-elsewhere  neither changes -> the wall is not terrain-grid geometry (a separate object or prop mesh); find its draw path
Outcomes: per episode, the near-ring emitted tri count and LOD tier vs the flight distribution. Default stays retail.
