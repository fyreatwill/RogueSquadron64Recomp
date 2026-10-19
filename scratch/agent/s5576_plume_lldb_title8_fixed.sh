#!/bin/zsh
set -u
ROOT=$(git -C "${0:A:h}" rev-parse --show-toplevel)
OUT="$ROOT/scratch/agent/soak_results/s5576_plume_lldb_title8_fixed"
BUILD="$ROOT/build"
mkdir -p "$OUT"
COMMON=(ROGUESQ_OVL2C_DROP=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_AUDIO_UCODE=1)
pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1 || true
bad=0; titles=0; N=8

control="$OUT/control.log"
/usr/bin/lldb -b -o run -- /bin/echo LLDB_CTL_OK > "$control" 2>&1 &
cp=$!
for i in $(seq 1 20); do grep -aq LLDB_CTL_OK "$control" && break; kill -0 "$cp" 2>/dev/null || break; sleep 1; done
kill -KILL "$cp" 2>/dev/null || true
if grep -aq LLDB_CTL_OK "$control"; then echo control=PASS >> "$OUT/summary"; else echo control=FAIL >> "$OUT/summary"; exit 1; fi

for r in $(seq 1 $N); do
  L="$OUT/run$r.lldb"; G="$OUT/run$r.game"
  /usr/bin/lldb -b -o 'process attach -n RogueSquadron64Recomp -w' -o 'process handle SIGSEGV -s true -n true -p true' -o 'process handle SIGBUS -s true' -o continue -o 'bt 30' -o 'register read' -o 'thread list' > "$L" 2>&1 &
  lp=$!
  sleep 2
  (cd "$BUILD" && exec env "${COMMON[@]}" ./RogueSquadron64Recomp) > "$G" 2>&1 &
  gp=$!
  for i in $(seq 1 45); do
    grep -aq 'origin=0x00790400' "$G" && break
    grep -aqE 'stop reason = (EXC_BAD|signal SIG(SEGV|BUS|ABRT))' "$L" && break
    kill -0 "$gp" 2>/dev/null || break
    sleep 1
  done
  grep -aq 'origin=0x00790400' "$G" && titles=$((titles+1))
  grep -aq 'plume-null-color-attachment' "$G" && { echo "run$r BREADCRUMB" >> "$OUT/summary"; bad=1; }
  grep -aqE 'stop reason = (EXC_BAD|signal SIG(SEGV|BUS|ABRT))' "$L" && { echo "run$r STOP" >> "$OUT/summary"; bad=1; }
  kill -KILL "$gp" "$lp" 2>/dev/null || true
  wait "$gp" 2>/dev/null || true
  wait "$lp" 2>/dev/null || true
done
echo "titles=$titles/$N bad=$bad" >> "$OUT/summary"
exit "$bad"
