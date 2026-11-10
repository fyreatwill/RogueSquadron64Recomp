# NEXT: qualify WIDEWIN cap 9216 for the 21:9 dd6 bundle on L1/L4 frozen poses (last cheap 21:9 L12 lever), else close the thread
HYPOTHESIS-ID: dd6-bundle-219-l12-cost
Context: s7051 reverted the s7050 21:9 K=0.5 default (L4 far horizon shaved 0.33, by eye). L12 21:9 bundle at K0.6 = ~58.6-59 fps (s7048/s7050).
s7049: cap 9216 vs 10240 on L12 21:9 = +0.5/+0.5 fps, poses 0.00 (cap8192 = 13.4, visible). Not checked on L1/L4.
Hypotheses: H-clean (cap9216 vs cap10240 <=0.1 at every L1/L4 pose while cap8192 control is visible) -> fold
ROGUESQ_DD_WIDEWIN_CAP=9216 for FB_WIDTH>796 into the s7037 bundle (setenv overwrite=0) / H-visible (>0.3 anywhere) -> close the
21:9 L12 cost thread at ~59 fps, no default change, pick the next ladder rung (CURRENT-TRUTH Next steps; owner-look items need no runs).
Unit (no build unless H-clean):
1. copy scratch/s7051/run.zsh -> scratch/s7052/run.zsh; arms c10240 (auto) / c9216 (+ROGUESQ_DD_WIDEWIN_CAP=9216) / c8192 ctl (=8192);
   remove the explicit CAP=10240 from the common string for the latter two; `zsh run.zsh 1; zsh run.zsh 4` (~30 min, sequential).
2. score: tools/s7032_pose_cull_score.py scratch/s7052/L<LV> --base c10240. L4 band location check like s7051 (rows/cols of >24 px).
3. If H-clean: edit main.cpp s7037 block, rebuild, boot check [s7037]/[ddbundle] cap line at 21:9 and 16:9 (16:9 must keep 10240).
