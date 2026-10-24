# NEXT: G1c - far-clip/frustum/fog hiding extra cells (H-hidden)
HYPOTHESIS-ID: g1c-draw-distance
s6059: poolx2 restores HUD partially at dd1.5 (126/203), terrain still no gain. px4_dd2 soak queued; fold it first: `python3 tools/g1c_ddtog_fold.py scratch/agent/m6/g1_lvl1g1cpx4_dd2 4500 --hud` (check [poolx] cap line).
1. If px4 restores HUD fully at dd2 yet terrain fraction flat: extra cells are submitted but invisible -> locate far-clip/frustum constant or fog in terrain submit path (L-radius/L-fade), one discriminator, ROGUESQ_FORCE_FOG control.
2. If HUD still lost at px4: next truncator is RSP DL/vertex/DMEM buffer.
3. Default stays retail.
