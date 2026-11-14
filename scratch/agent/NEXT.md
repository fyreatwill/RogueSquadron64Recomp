# NEXT (s7328): visible effect of the s7327 25-bit RSP DMA fix + dd6 RCP check
HYPOTHESIS-ID: spill-rcp-dma-width
Context (s7327): on the dd8 16:9 hangar route the gfx ucode DMAs terrain grid-layer data (initGridLayerFromLevelData, inside the spill
0x2DFF00 level buffer) at 0x81xxxxxx; the old 0xFFFFF8 mask read the 0x80xxxxxx alias (49152/49152 reads wrong). Fix default on:
rs64_s7327_mask in lib/N64ModernRuntime rsp.hpp, ROGUESQ_RSP_DMA25=0 old.
Hypotheses: H-visible (wrong grid data drew wrong/missing terrain cells in dd8 hangar-route missions; fix changes the frame) vs H-masked
(the bytes feed something that does not reach the frame, e.g. a cull/LOD table the CPU already resolved).
Discriminating measurement, one build, same pose: pose-locked capture (ROGUESQ_POSE_LOCK=1 + POSE_FREEZE, tools/g3_optin_pose_arms.sh,
tools/s7308_pose_horizon.py) on the dd8 16:9 hangar route in-mission, arms DMA25=1 / DMA25=0 / DMA25=1 repeat. Repeat arm must be
pixel-identical to arm 1 (control); arm 0 vs 1 diff > repeat diff selects H-visible, = selects H-masked. Also RDP triangle count
in the frame. Owner sheet if H-visible.
Also in the same session: RCPREF=ctl + DMA25_CTL=1 on the dd6 21:9 route (scratch/s7326/run.zsh s7328_dd6 "ROGUESQ_DRAW_DISTANCE=6
ROGUESQ_S7324_RCPREF=ctl ROGUESQ_RSP_DMA25_CTL=1", SECS=330): are the 0x19DF70 spill blocks RSP-read? Add a negative control for the
byte comparer (log a bit-24 read whose images match, or compare a spill block against itself).
Parallel open (item 22): 46 audio reads of song-channel arrays freed 0-14 ms earlier at the scene transition.
