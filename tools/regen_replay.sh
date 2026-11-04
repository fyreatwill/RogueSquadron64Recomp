#!/bin/zsh
# s6863: the whole post-N64Recomp chain for one tree. The steps after the fixer used to live only in scratch scripts.
# usage: tools/regen_replay.sh <RecompiledFuncs dir> [log]   (pristine N64Recomp output; never point it at a patched tree)
cd "$(dirname "$0")/.." || exit 2
D=$1; LOG=${2:-/dev/stdout}; [ -d "$D" ] || { echo "usage: $0 <dir> [log]"; exit 2; }
for step in fixup_game_funcs_vendored fixup_movz_movn strip_diag_layers fixup_live_replay weaken_patched_funcs; do
  python3 tools/$step.py "$D" >> "$LOG" 2>&1 || { echo "regen_replay: $step failed (see $LOG)"; exit 1; }
done
echo "regen_replay: ok"
