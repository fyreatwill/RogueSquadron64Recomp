# Next: fold s6316 calibration soak, choose fade centre, move hook to cell level
HYPOTHESIS-ID: g3c-owner-visual
Soak s6316_g3c_cal writes scratch/agent/m6/g1_lvl1s6316_cal/run.log with [edgefade4] lines.
1. Read [edgefade4]: does *slot (obj=) show plausible float position (x,y,z in game units, changing)? Does cell=x,z vary across the visible grid? Compare cell idx range to obj pos/scale to get the grid cell size.
2. Fix: A6C0 gets only a normal, so compute fade factor per cell in 0x8004AA94 (cell idx from s3+0x18/0x1A vs player cell) and store in a global read by the A6C0 epilogue hook (s3 = ctx->r19 may also work if preserved; verify cell != -1 in log).
3. Rerun dd3_log vs dd3_fade (reuse s6315 recipe), score with tools/g3c_edge_score.py; positive control f>0 count + visible tint. Then haze colour, send PNGs to owner.
