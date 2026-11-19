#!/bin/zsh
# s7617 G6a rumble proof: L12 dd4 forced route (s7516 ctl arm saw Start/Stop pulses there by t~85). Arms:
#  on     default (pak reported, rumble on) + virtual test pad whose Rumble callback witnesses SDL delivery
#  off    ROGUESQ_RUMBLE=0 (old shape: no pak) -> 0 motor calls, 0 vpad nonzero
#  offctl ROGUESQ_RUMBLE=0 + PAK_SHAPE_CTL=1 -> motor pulses arrive, 0 SDL rumble (output gate)
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
R=${R:-$PWD/scratch/s7617}; mkdir -p $R; rm -f $R/ok_*(N) $R/ring_*.txt(N)
E=ROGUESQ_FORCE_SAVE_MISSION=4+ROGUESQ_LOG_RUMBLE=1+ROGUESQ_RUMBLE_TEST=1+ROGUESQ_LOG_PAK_SHAPE=1
env R=$R HOLD=${HOLD:-200} DONE=quiet.done ARMS="1:on:$E 1:off:$E+ROGUESQ_RUMBLE=0+ROGUESQ_PAK_SHAPE_CTL=1" zsh tools/g1e_owner_quiet_arms.zsh | tee $R/out.txt; rc=${pipestatus[1]}
(( rc == 2 )) && exit 2
for a in on off; do echo "$a: $(grep '\[rumble\] sum' $R/log_$a.txt | tail -1)"; done | tee -a $R/out.txt
exit $rc
