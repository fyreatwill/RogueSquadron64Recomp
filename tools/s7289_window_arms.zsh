#!/bin/zsh
# s7289: which limit binds the dd>=4 terrain window (s7286: cells/call flat dd4..dd8)? ROGUESQ_G3E_TRACE site 17 = (ww, w, d, cap) per
# placed window. Arms 16:9 owner path (WIDEWIN auto stack): L4 dd2/dd4/dd6, L12 dd6, and a WIDEWIN=0 dd4 control (w,d must sit at <=64).
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
R=$PWD/scratch/s7289; rm -f $R/quiet.done $R/void_*(N)
W="ROGUESQ_FULLSCREEN=0+ROGUESQ_ASPECT=16:9+ROGUESQ_RETINA=0+ROGUESQ_G1B=1+ROGUESQ_STORE_DIAG=0+ROGUESQ_DD_UNSAFE=1+ROGUESQ_DD_MELT=1"
L4="ROGUESQ_FORCE_SAVE_MISSION=4+$W"; L12="ROGUESQ_FORCE_SAVE_MISSION=12+$W"
T="ROGUESQ_G3E_TRACE=$R/tr_"
env RESUME=1 VOID_OK_AFTER=110 R=$R HOLD=${HOLD:-150} DONE=quiet.done ARMS="2:l4d2:$L4+ROGUESQ_DD_WIDEWIN=1+${T}l4d2.txt 4:l4d4:$L4+ROGUESQ_DD_WIDEWIN=1+${T}l4d4.txt 6:l4d6:$L4+ROGUESQ_DD_WIDEWIN=1+${T}l4d6.txt 6:l12d6:$L12+ROGUESQ_DD_WIDEWIN=1+${T}l12d6.txt 4:l4c64:$L4+ROGUESQ_DD_WIDEWIN=0+${T}l4c64.txt" zsh tools/g1e_owner_quiet_arms.zsh; echo rc=$?
