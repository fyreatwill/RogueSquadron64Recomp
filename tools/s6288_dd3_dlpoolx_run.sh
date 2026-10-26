#!/bin/zsh
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1; sleep 2
ROGUESQ_G1B=1 XENV_EXTRA="ROGUESQ_G1CF=1 ROGUESQ_DD_UNSAFE=1 ROGUESQ_DLPOOLLOG=1 ROGUESQ_DLPOOLX=1 ROGUESQ_DLPOOLX_MB=2 ROGUESQ_DLPOOLX_AT=3000 ROGUESQ_UCODE_CAP=262144 ROGUESQ_DD_POOLX=4 ROGUESQ_BIGARENA=1 ROGUESQ_DRAW_DISTANCE=3 " HOLD_S=420 LEVEL=1 TAG_SUFFIX=s6288c zsh scratch/agent/g1_level_coverage_common.zsh > scratch/agent/s6288c.out 2>&1
echo done > scratch/agent/s6288c_done
