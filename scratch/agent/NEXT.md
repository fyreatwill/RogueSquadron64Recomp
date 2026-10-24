# NEXT: G1c - did raising the stream-pool cap un-break dd>=1.5?
HYPOTHESIS-ID: g1c-draw-distance
s6058: s6057 arms folded: dd1.25 HUD intact 202/202 but terrain gain nil (0.0795 vs 0.0813); dd1.5 HUD lost in 38/100 frames, terrain nil. Pool = malloc(cap*0x18) at loadLevelAssets, cap from level table 0x800B090C. Built ROGUESQ_DD_POOLX=<k> (tools/apply_s6058_poolx.py) scaling the cap+alloc.
1. Fold queued arms: `python3 tools/g1c_ddtog_fold.py scratch/agent/m6/g1_lvl1g1c{px2_dd2,px2_dd15,px4_dd2} 4500 --hud`. Check log shows `[poolx] cap A -> B` (control). HUD restored + terrain gain => pool cap was the truncator: then check pixels grow; HUD still lost => truncator is elsewhere (RSP DL/vertex/DMEM buffers, RT64 limit).
2. Even with HUD intact at 1.25 terrain does not grow: extra cells submitted but not visible => look at far-clip/frustum cull or fog/hidden by LOD (H-hidden).
3. Default stays retail. No macOS timeout. FBD_EVERY_V is the dump rate.
