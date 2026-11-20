#!/bin/zsh
# s7680 G6c: does the s7679 near release (ROGUESQ_S7679_NEAR) fire in FLIGHT? Forced level, owner recipe dd4 16:9 FPS60,
# STANDINS=1 LOG=1 HOLD=odd, 200 s, two arms in one invocation (sequential, one game at a time):
#   x<L> = default near (15)   c<L> = positive control NEAR=99 (must release held stand-ins; held count must collapse).
# usage: zsh tools/s7680_flight_release.zsh <outdir> <level 0-based>
# rc 0 = both alive, default arm 0 releases, control >0 releases; rc 1 otherwise. Prints counts + s7675 ghost score per arm.
cd "$(git rev-parse --show-toplevel)" || exit 1
S=${1:A}; L=${2:-5}; mkdir -p $S
E="ROGUESQ_STANDINS=1+ROGUESQ_STANDINS_LOG=1+ROGUESQ_S7672_HOLD=odd"; (( L != 1 )) && E="$E+ROGUESQ_FORCE_SAVE_MISSION=$L"
env R=$S HOLD=200 ALLOW_SLOW=1 ARMS="4:x$L:$E 4:c$L:$E+ROGUESQ_S7679_NEAR=99" zsh tools/g1e_owner_quiet_arms.zsh; rc=$?
nx=$(grep -c '^\[s7679-rel\]' $S/log_x$L.txt 2>/dev/null); nc=$(grep -c '^\[s7679-rel\]' $S/log_c$L.txt 2>/dev/null)
for a in x$L c$L; do python3 tools/s7675_ghost_score.py $S/log_$a.txt | grep -E '^never|^==' ; done
echo "s7680 level=$L rel_default=${nx:-na} rel_control=${nc:-na} arms_rc=$rc"
(( rc == 0 && ${nx:-1} == 0 && ${nc:-0} > 0 )) && exit 0; exit 1
