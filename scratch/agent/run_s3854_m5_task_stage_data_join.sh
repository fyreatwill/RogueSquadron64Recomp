#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=$ROOT/scratch/agent/s3854_m5_task_stage_data_join
mkdir -p "$OUT"
ORACLE=$ROOT/tools/oracle/build/rs64_oracle
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
if [[ ! -x "$ORACLE" || ! -f "$CORE" || ! -f "$ROM" || ! -f "$VIDEO" ]]; then
  print -r -- setup_missing > "$OUT/driver.log"
  exit 2
fi
PRESS='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start'
cd "$ROOT" || exit 2
env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 75 \
  --watch-write 0x0:0x800000 --watch-write 0x167000:0x169B00 \
  --watch-write 0x173CB0:0x173DB0 --watch-write 0x1798B0:0x179A48 \
  --watch-write 0x149470:0x1494B0 \
  --watch-pc 0x80033FCC,0x80019DEC,0x80019D68,0x80015BC8,0x8000F3A0 \
  --pc-task-dump 0x80033FCC --pc-task-type 2 --pc-task-join \
  --pc-field-dump 0x80015BC8,0x8000F3A0 \
  --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 \
  --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 \
  --pc-hist-watch 1 --pc-hist-watch 4 --post-value-watch 4 \
  --post-value-pc 0x80091718,0x8009172c,0x8009173c,0x80091748,0x80091758,0x80091764,0x8009176c,0x80091774,0x8009177c,0x80091784 \
  --post-value-pc-detail --vi-trace --hit-cap 20 --press "$PRESS" --hold-ms 150 \
  > "$OUT/retail.log" 2>&1 &
retail=$!
cd "$ROOT/build" || exit 2
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_DRAIN_INLOOP_TICK=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a' \
  PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 ROGUESQ_LOG_PHASE=1 \
  ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_TASK_LIFETIME=1 \
  ROGUESQ_LOG_M5_STAGE_CALLS=1 ROGUESQ_LOG_M5_STAGE_BYTES=1 \
  ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 \
  ROGUESQ_LOG_M5_EXACT_ROUTE=1 ROGUESQ_LOG_M5_SOURCE_RANGE=1 \
  ROGUESQ_LOG_M5_ROUTE_PREPARE=1 ROGUESQ_LOG_M5_ROUTE_HANDOFF=1 \
  ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp > "$OUT/port.log" 2>&1 &
port=$!
print -r -- "retail=$retail port=$port" > "$OUT/driver.log"
for tick in {1..360}; do
  alive=0; kill -0 "$retail" 2>/dev/null && alive=1; kill -0 "$port" 2>/dev/null && alive=1
  (( alive )) || break
  sleep 0.25
done
kill -KILL "$retail" "$port" 2>/dev/null || true
wait "$retail" 2>/dev/null || true
wait "$port" 2>/dev/null || true
for marker in 'positive-control threshold reached' 'origin=0x00790400 width=1024' 'origin=0x006ab400 width=512' '[pc-task-dump]' '[pc-task-join]' '[pc-field-row]' 'exec pc=0x80015bc8' 'exec pc=0x8000f3a0' '[oracle] pc-hist-phase' '[oracle] writer-pc-phase' '[oracle] done:'; do
  print -r -- "retail_${marker// /_}=$(grep -a -F -c "$marker" "$OUT/retail.log" || true)" >> "$OUT/driver.log"
done
for marker in '[phase]' '[audtask-abi]' '[audtask-image-stage]' '[audtask-image-dma-join]' 'CRASH' 'ABORT'; do
  print -r -- "port_${marker// /_}=$(grep -a -F -c "$marker" "$OUT/port.log" || true)" >> "$OUT/driver.log"
done
awk '
function field(name, i) { for (i=1; i<=NF; ++i) if (index($i,name "=")==1) return substr($i,length(name)+2); return "" }
function norm(s) { sub(/^0[xX]/,"",s); return tolower(s) }
$1=="[pc-task-dump]" { ++task; key=norm(field("data_ptr")) ":" norm(field("data_size")); task_key[key]++; next }
$1=="[pc-task-join]" { ++join; key=norm(field("data_ptr")) ":" norm(field("data_size")); join_key[key]++; next }
$1=="[pc-field-row]" { ++fieldrow; next }
END {
  print "task_rows=" task " task_pointer_keys=" length(task_key) " joined_rows=" join " field_rows=" fieldrow;
  for (k in task_key) print "task_key=" k " task_rows=" task_key[k] " joined_rows=" (join_key[k]+0)
}' "$OUT/retail.log" > "$OUT/retail_join.txt"
