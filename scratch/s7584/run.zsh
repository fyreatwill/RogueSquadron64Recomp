#!/bin/zsh
# s7584 class UI: uninitialized-read witness, owner recipe. GD=build_autoinit (pattern) or build_autoinitz (zero); TAG names the run dir.
# Every arm runs MallocScribble=1 (heap 0xAA on alloc, 0x55 on free); arm 1 also fires plant 7 (stack+heap control).
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
GD=${GD:-build_autoinit}; R=$PWD/scratch/s7584/${TAG:-pat}; mkdir -p $R; rm -f $R/quiet.done $R/ok_*(N)
env R=$R HOLD=${HOLD:-150} ALLOW_SLOW=1 DONE=quiet.done GAMEDIR=$GD ARMS="4:l1:MallocScribble=1+ROGUESQ_S7578_PLANT=7 2:l4:ROGUESQ_FORCE_SAVE_MISSION=4+MallocScribble=1 4:l12:ROGUESQ_FORCE_SAVE_MISSION=12+MallocScribble=1" zsh tools/g1e_owner_quiet_arms.zsh | tee $R/out.txt
exit ${pipestatus[1]}
