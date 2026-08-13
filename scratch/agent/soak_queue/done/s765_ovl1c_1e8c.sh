#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT="$ROOT/scratch/agent/soak_results/s765_ovl1c_1e8c_$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT"
cd "$ROOT/build"
set +e
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
    ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_E9_PROVENANCE=1 \
    ROGUESQ_LOG_FL_ZERO_WATCH=1 ROGUESQ_LOG_CIMG_RAW=1 ROGUESQ_LOG_DL_SYNC2=1 \
    PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 \
    PROBE_LEAVE_OK=1 \
    PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' \
    zsh ../tools/probe.sh "$OUT" 300 2
PRC=$?
set -e
LOG="$OUT/run.log"
echo "probe_rc=$PRC out=$OUT"
if ! grep -aq '\[phase\] vi_width=1024' "$LOG"; then
  echo "EARLY-DEATH: no VI 1024"
  grep -E '\[CRASH\]|SIGBUS|SIGSEGV|last-guest-pc|pc-symbol' "$LOG" | tail -20 || true
  exit 4
fi
fail=0
for p in \
  '\[ovl-route\].*res=0x20 tgt=0x12A0' \
  '\[ovl-route\].*res=0x24 tgt=0x12A0' \
  '\[ovl-route\].*res=0x1C tgt=0x1E7C' \
  '\[ovl-route\].*res=0x04' 'dl06='; do
  grep -aqE -- "$p" "$LOG" && echo "CTRL OK $p" || { echo "CTRL FAIL $p"; fail=1; }
done
echo "=== UJ leftovers ==="
grep -o 'Unhandled jump target 0x[0-9A-Fa-f]*' "$LOG" | sort | uniq -c | sort -rn || true
echo "=== ovl-route last n ==="
for p in 'res=0x20 tgt=0x12A0' 'res=0x24 tgt=0x12A0' 'res=0x1C tgt=0x1E7C' \
         'res=0x1C tgt=0x1E8C' 'res=0x1C tgt=0x1ECC' 'res=0x04'; do
  c=$(grep -c -- "$p" "$LOG" || true)
  last=$(grep -- "$p" "$LOG" | tail -1 | grep -oE 'n=[0-9]+' | head -1)
  echo "  $p count=$c last=$last"
done
echo "=== clip-stray / CRASH / dl06 ==="
grep -c '\[clip-stray\]' "$LOG" || true
grep -c '\[CRASH\]' "$LOG" || true
grep -o 'dl06=push:[0-9]*,complete:[0-9]*,open:[0-9]*' "$LOG" | head -4
echo "=== E9 match / rdpFs ==="
grep -oE 'match=[0-9]+/[0-9]+' "$LOG" | tail -5 || true
grep -oE 'rdpFs=[0-9]+' "$LOG" | head -1 || true
grep -oE 'rdpFs=[0-9]+' "$LOG" | tail -1 || true
echo "$OUT"
exit $fail
