#!/bin/zsh
# s7672 G6c stand-in -> real object handoff. usage: zsh scratch/s7672/run.zsh <outdir> <level 0-based, 1=default route> [HOLD mode: 1|0|odd] [DD, default 4 (s7799)]
# Owner recipe dd4 16:9 FPS60, STANDINS=1 + LOG=1, 200 s hold; score with tools/s7672_handoff_score.py <outdir>/log_<arm>.txt (rc 1 = a held stand-in blinked).
cd "$(git rev-parse --show-toplevel)" || exit 1
S=${1:A}; L=${2:-1}; H=${3:-odd}; DD=${4:-4}; mkdir -p $S
E="ROGUESQ_STANDINS=1+ROGUESQ_STANDINS_LOG=1+ROGUESQ_S7672_HOLD=$H"; (( L != 1 )) && E="$E+ROGUESQ_FORCE_SAVE_MISSION=$L"
env R=$S HOLD=200 ALLOW_SLOW=1 ARMS="$DD:x$L:$E" zsh tools/g1e_owner_quiet_arms.zsh; rc=$?
python3 tools/s7672_handoff_score.py $S/log_x$L.txt; exit $(( rc ? rc : $? ))
