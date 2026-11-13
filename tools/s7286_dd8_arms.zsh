#!/bin/zsh
# s7286: G1c phase 2 dd8 on the owner path (16:9, FPS60 default, WIDEWIN auto stack R=88). Arms L4 dd6 ref / dd8 / dd8+DUTY1.4 control, L12 dd6 / dd8.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
R=$PWD/scratch/s7286; rm -f $R/quiet.done $R/void_*(N)
W="ROGUESQ_FULLSCREEN=0+ROGUESQ_ASPECT=16:9+ROGUESQ_RETINA=0+ROGUESQ_G1B=1+ROGUESQ_STORE_DIAG=0+ROGUESQ_DD_UNSAFE=1+ROGUESQ_DD_MELT=1+ROGUESQ_DD_WIDEWIN=1"
L4="ROGUESQ_FORCE_SAVE_MISSION=4+$W"; L12="ROGUESQ_FORCE_SAVE_MISSION=12+$W"
env RESUME=1 VOID_OK_AFTER=110 R=$R HOLD=240 DONE=quiet.done ARMS="6:l4d6:$L4 8:l4d8:$L4 8:l4d8c:$L4+DUTY=1.4 6:l12d6:$L12 8:l12d8:$L12" zsh tools/g1e_owner_quiet_arms.zsh; echo rc=$?
