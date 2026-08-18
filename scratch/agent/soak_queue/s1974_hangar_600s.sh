#!/bin/zsh
# s1974 soak: 600s hangar stability check with all spin-yield gates active.
# Establishes a 600s baseline and looks for new crash families.
set -e
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
cd "$ROOT"
OUT="$ROOT/scratch/agent/soak_results/s1974_hangar_600s_$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT"

env ROGUESQ_SPIN_YIELD=1 \
    ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
    ROGUESQ_STUB_MISSING_FUNCS=1 \
    PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
    PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
    zsh tools/probe.sh "$OUT" 600 2
rc=$?

frames=$(ls "$OUT"/f_*.png 2>/dev/null | wc -l | tr -d ' ')
crashes=$(grep -c '\[CRASH\]' "$OUT/run.log" 2>/dev/null || echo 0)
fs_frozen=$(grep -E '^\[vi\].*fs=1[0-9]{3}' "$OUT/run.log" 2>/dev/null | awk -F'fs=' '{print $2}' | awk '{print $1}' | sort -u | wc -l | tr -d ' ')

echo "s1974_hangar_600s: rc=$rc frames=$frames crashes=$crashes fs_unique_vals=$fs_frozen" >> "$ROOT/scratch/agent/SOAK-RESULTS.md"
exit $rc
