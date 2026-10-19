#!/bin/zsh
# s5532: fixup-stage determinism. pristine N64Recomp output -> vendored fixer (scratch dir) -> diff vs live tree.
# Positive control: perturb one scratch file, confirm the diff flags it. Never touches the live tree.
cd "$(dirname "$0")/../.." || exit 2
SRC=../N64Recomp/RecompiledFuncs.s4204-fresh
LIVE=../N64Recomp/RecompiledFuncs
D=../N64Recomp/scratch_s5532; rm -rf "$D"; ditto $SRC "$D" || exit 3
python3 tools/fixup_game_funcs_vendored.py "$D" > scratch/agent/s5532_fixup.log 2>&1
python3 tools/fixup_movz_movn.py "$D" >> scratch/agent/s5532_fixup.log 2>&1  # s5534: movz/movn replay
python3 tools/strip_diag_layers.py "$D" >> scratch/agent/s5532_fixup.log 2>&1  # s5535
python3 tools/fixup_live_replay.py "$D" >> scratch/agent/s5532_fixup.log 2>&1  # s5540
echo "fixup rc=$?"; grep 'failures=' scratch/agent/s5532_fixup.log
tot=0; for f in $LIVE/*; do b=${f:t}; n=$(diff "$D/$b" "$f" 2>&1 | grep -c '^[<>]'); [ "$n" -gt 0 ] && echo "$b $n"; tot=$((tot+n)); done | sort -k2 -nr > scratch/agent/s5532_diffsummary.txt
echo "files differing: $(wc -l < scratch/agent/s5532_diffsummary.txt)"; head -60 scratch/agent/s5532_diffsummary.txt
# positive control
cp "$D/funcs_26.c" /tmp/s5532_ctl.c; echo "// perturb" >> "$D/funcs_26.c"
echo "control funcs_26 diff lines: $(diff "$D/funcs_26.c" $LIVE/funcs_26.c | grep -c '^[<>]') (baseline above)"
