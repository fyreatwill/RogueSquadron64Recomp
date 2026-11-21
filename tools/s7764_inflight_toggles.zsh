#!/bin/zsh
# s7764: in-flight owner-queue toggles, 3 arms on L1 dd4 21:9 (def / off / tog), sequential, via g1e_owner_quiet_arms.
cd "$(git rev-parse --show-toplevel)" || exit 1
S=$PWD/scratch/s7764/runs; rm -rf $S; mkdir -p $S
L="ROGUESQ_ASPECT=21:9+ROGUESQ_LOG_RUMBLE=1+ROGUESQ_RUMBLE_TEST=1+ROGUESQ_W_SHEET_STATS=1+ROGUESQ_LOG_STICK_GATE=1+ROGUESQ_LOG_M5_B40_READ=1+ROGUESQ_FORCE_SAVE_MISSION=1"
OFF="ROGUESQ_RUMBLE=0+ROGUESQ_W_CLAMP=0+ROGUESQ_DD_FARMAX=0+ROGUESQ_HORIZON_SKYFILL=0+ROGUESQ_STICK_GATE=0+ROGUESQ_M5_B40_VALUE=1"
TOG="ROGUESQ_W_CLAMP=tog+ROGUESQ_HORIZON_SKYFILL=tog+ROGUESQ_RUMBLE_SCALE=0.5"
env R=$S HOLD=150 ALLOW_SLOW=1 ARMS="4:def:$L 4:off:$L+$OFF 4:tog:$L+$TOG" zsh tools/g1e_owner_quiet_arms.zsh
S2=$PWD/scratch/s7764/b40; rm -rf $S2; mkdir -p $S2
env R=$S2 HOLD=70 ALLOW_SLOW=1 ARMS="4:b0:ROGUESQ_LOG_M5_B40_ROUTE=1+ROGUESQ_FORCE_SAVE_MISSION=1 4:b1:ROGUESQ_LOG_M5_B40_ROUTE=1+ROGUESQ_M5_B40_VALUE=1+ROGUESQ_FORCE_SAVE_MISSION=1" zsh tools/g1e_owner_quiet_arms.zsh
python3 tools/s7764_inflight_toggle_check.py $S
