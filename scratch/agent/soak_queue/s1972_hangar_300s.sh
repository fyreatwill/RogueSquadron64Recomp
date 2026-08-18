#!/usr/bin/env zsh
# s1972 soak: 300s hangar stability check with all three spin-yield gates active.
# Verifies the 180s stable window extends further and no new crash families appear.
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT="$ROOT/scratch/agent/soak_results/s1972_hangar_300s_$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT"
cd "$ROOT/build"

env ROGUESQ_SPIN_YIELD=1 \
    ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
    ROGUESQ_STUB_MISSING_FUNCS=1 \
    PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=300 PROBE_LEAVE_OK=1 \
    PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
    zsh "$ROOT/tools/probe.sh" "$OUT" 300 2 >"$OUT/run.log" 2>&1
rc=$?

frames=$(ls "$OUT"/*.png 2>/dev/null | wc -l | tr -d ' ')
crashes=$(grep -c 'SIGBUS\|SIGSEGV\|last-guest-pc' "$OUT/run.log" 2>/dev/null || true)
audiodrain=$(grep 'site=audioDrain' "$OUT/run.log" 2>/dev/null | wc -l | tr -d ' ')
echo "s1972_hangar_300s: rc=$rc frames=$frames crashes=$crashes audioDrain_yields=$audiodrain" >> "$ROOT/scratch/agent/SOAK-RESULTS.md"
exit $rc
