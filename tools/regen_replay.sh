#!/bin/zsh
# s6863: the whole post-N64Recomp chain for one tree. The steps after the fixer used to live only in scratch scripts.
# usage: tools/regen_replay.sh <RecompiledFuncs dir> [log]   (pristine N64Recomp output; never point it at a patched tree)
cd "$(dirname "$0")/.." || exit 2
D=$1; LOG=${2:-/dev/stdout}; [ -d "$D" ] || { echo "usage: $0 <dir> [log]"; exit 2; }
for step in fixup_game_funcs_vendored fixup_movz_movn strip_diag_layers fixup_live_replay weaken_patched_funcs fixup_cut_decoded_tails; do
  python3 tools/$step.py "$D" >> "$LOG" 2>&1 || { echo "regen_replay: $step failed (see $LOG)"; exit 1; }
done
# s6868: last, so every fixer above still sees the names N64Recomp emitted.
python3 tools/rename_generated_symbols.py "$D" >> "$LOG" 2>&1 || { echo "regen_replay: rename failed (see $LOG)"; exit 1; }
# s7361: no injected MEM_x base may be zero-extended (lands 4 GB past rdram).
python3 tools/s7361_memzext_census.py --gen "$D" >> "$LOG" 2>&1 || { echo "regen_replay: s7361 zero-extended MEM base (see $LOG)"; exit 1; }
echo "regen_replay: ok"
