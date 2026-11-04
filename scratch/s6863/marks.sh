#!/bin/zsh
# s6863: where does each of the 9 MARKs vanish? Control: s4296 A14 yield must stay present at every stage.
cd "$(dirname "$0")/../.."
D=../N64Recomp/scratch_s6863_stage; rm -rf $D; ditto ../N64Recomp/scratch_s5547_regen $D
M=("PATCH: s2463 m5 dynamic callback tuple" "PATCH: s4221 coef" "PATCH: s4222 vol" "PATCH: s4223 stk" "PATCH: s4300 rsfree bt" "PATCH: s4466 hdrdump" "PATCH: s4560 nulldump" "PATCH: s4602 rs_strncpy caller table" "PATCH: s4680 status table store" "s4296 A14")
show() { echo "== $1"; for m in $M; do echo "$(cat $D/*.c | grep -c "$m") $m"; done; }
python3 tools/fixup_game_funcs_vendored.py $D > /dev/null 2>&1; echo rc=$?; show fixer
python3 tools/fixup_movz_movn.py $D >/dev/null 2>&1; python3 tools/strip_diag_layers.py $D > /dev/null 2>&1; show strip
python3 tools/fixup_live_replay.py $D > /dev/null 2>&1; show live_replay
