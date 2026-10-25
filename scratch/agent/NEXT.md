# NEXT: G1d step 36 - terrain left-edge void at 21:9, then HUD edge anchoring
HYPOTHESIS-ID: g1d-widescreen
s6143 verified ROGUESQ_ASPECT=21:9 -> w1024 flight (scratch/agent/m6/s6143/a219_w1024.png). Defects: sky-blue void left of the terrain (terrain visibility/cull uses 4:3 frustum? or tile radius) and HUD not edge-anchored.
Work unit: one build with a cull-bypass/log for the terrain patch visibility test; compare w1024 vs 4:3 ctl; H-frustum (terrain cull uses 4:3 FOV/aspect) vs H-radius (distance) vs H-camera-angle (void is just sky at that heading). Positive control: widen the cull and see terrain fill. Recipe: s6143_run.sh. Then HUD x anchoring, menus/hangar at wide.
