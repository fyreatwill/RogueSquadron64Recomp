#!/bin/zsh
# s7753 (from scratch/s7751/run.zsh, s7751): re-capture the s7753 gate snaps.
# s7751: L1 21:9 dd8 same-pose FARMAX=0 (pinned sliver) and default arms with the gfx task snapshot armed (ROGUESQ_S7751_SNAP).
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
S=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/s7751
C="ROGUESQ_ASPECT=21:9+ROGUESQ_FULLSCREEN=0+ROGUESQ_RETINA=0+ROGUESQ_DD_UNSAFE=1+ROGUESQ_DD_WIDEWIN=1+ROGUESQ_DD_MELT=1+ROGUESQ_DRAW_DISTANCE=8+ROGUESQ_G5B_FRAME_EVERY=1000+ROGUESQ_G5B_FRAME_MAX_MB=1600"
env LEVEL=1 PIN=1 TAGP=s7751 FZ=106.28 zsh tools/g3_optin_pose_arms.sh scratch/s7751/a1 \
  l1f0=$C+ROGUESQ_DD_FARMAX=0+ROGUESQ_G5B_FRAME_FROM=4030+ROGUESQ_G5B_FRAME=$S/l1f0.cap+ROGUESQ_S7751_SNAP=$S/snap_f0 \
  l1d=$C+ROGUESQ_G5B_FRAME_FROM=4030+ROGUESQ_G5B_FRAME=$S/l1d.cap+ROGUESQ_S7751_SNAP=$S/snap_d
echo ALLDONE
