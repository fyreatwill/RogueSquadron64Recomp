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
# s7362: no raw rdram + X in the injected tree or owned host code may leave the 4 GB reservation without a hand verdict.
python3 tools/s7362_rdramraw_census.py --gen "$D" --check >> "$LOG" 2>&1 && python3 tools/s7362_rdramraw_census.py --check >> "$LOG" 2>&1 || { echo "regen_replay: s7362 unreviewed raw rdram offset (see $LOG)"; exit 1; }
# s7363: no host fixed-size array in the injected tree or owned host code (+ rt64) may take an unproven subscript without a hand verdict.
python3 tools/s7363_hostarr_census.py --gen "$D" --check >> "$LOG" 2>&1 && python3 tools/s7363_hostarr_census.py --rt64 --check >> "$LOG" 2>&1 || { echo "regen_replay: s7363 unreviewed host-array subscript (see $LOG)"; exit 1; }
# s7364: no runtime-sized host buffer (vector/string/new[]/malloc) in the injected tree or owned host code (+ rt64) may take an unproven subscript or mem range without a hand verdict.
python3 tools/s7364_heapbuf_census.py --gen "$D" --check -q >> "$LOG" 2>&1 && python3 tools/s7364_heapbuf_census.py --rt64 --check -q >> "$LOG" 2>&1 || { echo "regen_replay: s7364 unreviewed heap-buffer subscript (see $LOG)"; exit 1; }
# s7365: no reference/pointer/iterator/index captured from a host container (+ rt64) may be used after an invalidating mutation, and no member index into a container cleared elsewhere, without a hand verdict.
python3 tools/s7365_invalidation_census.py --selftest >> "$LOG" 2>&1 && python3 tools/s7365_invalidation_census.py --check -q >> "$LOG" 2>&1 || { echo "regen_replay: s7365 unreviewed container-invalidation capture (see $LOG)"; exit 1; }
python3 tools/s7366_lockset_census.py --selftest >> "$LOG" 2>&1 && python3 tools/s7366_lockset_census.py --check >> "$LOG" 2>&1 || { echo "regen_replay: s7366 unreviewed mixed-lock container access (see $LOG)"; exit 1; }
echo "regen_replay: ok"
