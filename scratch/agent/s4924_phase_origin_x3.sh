#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT="$ROOT/scratch/agent/s4924_phase_origin_x3"
rm -rf "$OUT"
mkdir -p "$OUT"
cd "$ROOT/build" || exit 2

for run in 1 2 3; do
  pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1 || true
  log="$OUT/run_${run}.log"
  env ROGUESQ_OVL2C_DROP=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 \
    ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_DLWALK=1 ROGUESQ_LOG_E9_PROVENANCE=1 ROGUESQ_LOG_TASKSUBMIT=1 \
    ROGUESQ_LOG_PHASE=1 PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=240 \
    PROBE_LEAVE_OK=1 ./RogueSquadron64Recomp >"$log" 2>&1 &
  pid=$!
  trap 'kill -KILL "$pid" 2>/dev/null || true; pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1 || true' EXIT INT TERM

  sleep 240
  kill -KILL "$pid" >/dev/null 2>&1 || true
  wait "$pid" >/dev/null 2>&1 || true

  first=$(grep -a 'vi_width=512' "$log" | head -1 | sed -n 's/.*origin=0x\([0-9A-Fa-f]*\).*/0x\1/p')
  origins=$(grep -a 'vi_width=512' "$log" | sed -n 's/.*origin=0x\([0-9A-Fa-f]*\).*/0x\1/p' | sort | uniq | tr '\n' ',' | sed 's/,$//')
  controls=$(grep -ac 'vi_width=512' "$log")
  counter=$(grep -a '^\[vi\] update_screen' "$log" | tail -1 | sed -n 's/.*#\([0-9][0-9]*\).*/\1/p')
  crashes=$(grep -ac '\[CRASH\]\|\[ABORT\]' "$log")
  print "run=$run first_512=${first:-none} origins=${origins:-none} control_rows=$controls counter=${counter:-none} crashes=$crashes" | tee -a "$OUT/summary.txt"
done

pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1 || true
