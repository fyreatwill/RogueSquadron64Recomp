#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT="$ROOT/scratch/agent/s3839_m5_task_contract_input_dma_join"
mkdir -p "$OUT"
cd "$ROOT/build" || exit 2
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a' \
  PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 ROGUESQ_LOG_PHASE=1 \
  ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_TASK_LIFETIME=1 \
  ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 \
  ROGUESQ_LOG_M5_EXACT_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_PREPARE=1 \
  ROGUESQ_LOG_M5_ROUTE_HANDOFF=1 ROGUESQ_LOG_M5_RSP_SOURCE=1 \
  ROGUESQ_LOG_M5_STAGE_CALLS=1 ROGUESQ_LOG_M5_STAGE_BYTES=1 \
  ROGUESQ_LOG_M5_FAMILY_EDGE=1 ROGUESQ_LOG_M5_FAMILY_STORE=1 \
  ROGUESQ_LOG_M5_SOURCE_RANGE=1 ROGUESQ_LOG_M5_DYNAMIC_CALLBACK=1 \
  ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp >"$OUT/run.log" 2>&1 &
pid=$!
title=0
hangar=0
for tick in {1..720}; do
  if ! kill -0 "$pid" 2>/dev/null; then break; fi
  if (( title == 0 )) && grep -a -q '^\[phase\].*vi_width=1024.*origin=0x00790400' "$OUT/run.log"; then
    title=1
  fi
  if (( hangar == 0 )) && grep -a -q '^\[phase\].*vi_width=512.*origin=0x006AB400' "$OUT/run.log"; then
    hangar=1
    sleep 15
    break
  fi
  sleep 0.25
done
kill -KILL "$pid" 2>/dev/null || true
wait "$pid" 2>/dev/null || true
print -r -- "title=$title hangar=$hangar" > "$OUT/summary.txt"
for marker in phase audtask-abi audtask-dma-row audtask-dma-range m5-task-lifetime m5-host-task-boundary m5-task-handoff m5-rsp-source-hook-control m5-rsp-dma-census m5-source-range-reader m5-source-range-writer audtask-image-stage audio-return CRASH ABORT; do
  print -r -- "$marker=$(grep -a -F -c "[$marker]" "$OUT/run.log" || true)" >> "$OUT/summary.txt"
done
awk '
function v(name, i) { for (i=1; i<=NF; ++i) if (index($i,name "=")==1) return substr($i,length(name)+2); return "" }
function norm(s) { sub(/^0[xX]/,"",s); return tolower(s) }
$1=="[audtask-abi]" { ++abi; key=norm(v("data_ptr")) ":" norm(v("data_size")); abi_key[key]++; next }
$1=="[m5-task-lifetime]" { ++life; if (index($0,"words=")>0) { split(v("words"),w,","); k=norm(w[13]) ":" norm(w[14]); life_key[k]++ } next }
$1=="[audtask-dma-row]" { ++dma; k=norm(v("data_ptr")) ":" norm(v("data_size")); dma_key[k]++; next }
$1=="[audtask-dma-range]" { ++range; if (norm(v("dmem"))=="cb0" && norm(v("len"))=="198") ++exact; next }
END {
 print "join abi=" abi " lifetime=" life " dma_rows=" dma " dma_ranges=" range " exact_cb0_len198=" exact;
 for (k in abi_key) print "contract_key=" k " abi=" abi_key[k] " lifetime=" (life_key[k]+0) " dma=" (dma_key[k]+0)
}' "$OUT/run.log" > "$OUT/join.txt"
