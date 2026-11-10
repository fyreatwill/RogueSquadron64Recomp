# NEXT: FPS60 near-wall flicker: log the terrain builder's per-cell keep/cull decisions near the camera across an episode
HYPOTHESIS-ID: fps60-wall-terrain-cull
Context (s7103): the camera collision in applyPlayerVehicleStateUpdate does not explain the episodes. Corners are left inside at exit on
41% of clean lim1 flight ticks, several episodes have no corner inside, and the ROGUESQ_S7103_CAMFIX re-push arm leaves the episode rate
unchanged (5/2714 off vs 5/3738 on, P=0.42). s7098 showed the missing wall is absent from the game's own RDP stream, so the game decides
not to submit it. The terrain builder buildVisibleTerrainGridAroundCamera (s7101 bv hook at its entry, same CHASE file) reads the camera
matrix +0x4C..0x54. Find its per-cell visibility / cull tests (frustum, behind-camera, distance, LOD) by static read first.
Unit (one build, one run, scratch/s7099/arm.zsh 6 4 <tag> "... ROGUESQ_S7101_CHASE=<file>" 120 240):
 1. New tools/apply_s7104_cellcull.py: per builder call, for cells within ~3 cell widths of the camera: cell id/x,z, each cull test's inputs
    and verdict, and kept/submitted. One line per call with a compact kept-mask too, mach-stamped (episode alignment as s7103_residual.py).
 2. Positive control: the far cells culled by distance must show up as culled in normal flight (the test visibly fires).
Hypotheses:
 H-behind  a near wall cell whose centre/bbox sits behind the camera plane is culled while its wall faces are still on screen (camera hugging
           the wall puts the cell centre behind the eye) -> episode ticks show the wall cell flipping kept/culled with the camera's z/yaw
 H-frustum the cell bbox vs frustum test uses a stale or narrower (4:3, not the 16:9 wide) frustum -> the culled cells are at the screen side
 H-lod     the cell switches LOD / patch and the replacement has no wall faces for 1-3 frames -> kept, but the submitted mesh differs
 H-none    the builder keeps the cell on episode ticks -> the drop is later (display list / F5 ucode clip of the near polys); go to the DL
Outcomes: per episode, the wall cell's kept flag and which test removed it. Default stays retail.
Queued already (fold first): soak_queue/s7103_camfix_r1/r2 (same s7103 recipe, resid_r*.txt) for more CAMFIX episodes.
