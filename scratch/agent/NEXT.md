# NEXT: dd6 bundle image check on the load-bearing levels L12 and L13 (16:9 frozen poses)
HYPOTHESIS-ID: dd6-bundle-loadbearing-image
Context: s7041-s7043 held all levels 0-18 at the dd6 auto bundle (16:9) clean. On L12 (42.8 -> 59.7 fps) and L13 (48.3 -> 59.9)
the cull is load-bearing, so it removes the most cells there (ocull/f ~2900-3450) - yet image neutrality was only measured on L1/L4
poses (s7038/s7040) and the cutscene playlist (s7039). Those are the levels where a visible cut is most likely.
Unit: copy scratch/s7040/run.zsh to scratch/s7044/run.zsh (outdir scratch/s7044/L$LV, TAGP s7044L$LV, NOREF=1 path for both levels,
FZ "36 46 56 66 80 100 125 150"), run L12 then L13 (one game at a time, in background), score with tools/s7032_pose_cull_score.py
(base dd6off) exactly as s7040.
Hypotheses / outcomes:
- H-neutral: dd6b vs dd6off <=0.3 mean |dLum| at every pose, A/A dd6b vs dd6b2 ~0, dd4 vs dd6off positive control >=3 -> bundle qualified on
  the load-bearing levels; owner sheet of the worst pose per level.
- H-visible: some pose > 0.5 or frac>24 > 1% with A/A ~0 -> the cull cuts visible ground there; find the ring (K/R) and either raise K on
  those dims (88x88, 64x64) or gate it, re-measure cost.
- H-path: arms diverge ([posefreeze] pos differs) -> path not reproducible, use poseref on a reference arm instead.
