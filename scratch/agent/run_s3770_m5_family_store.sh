#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT="$ROOT/scratch/agent/s3770_m5_family_store"
mkdir -p "$OUT"
cd "$ROOT" || exit 2

env tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 75 --watch-write 0x0:0x800000 \
  --watch-write 0x178C80:0x178F80 --watch-write 0x1797B0:0x179A48 \
  --pc-phase-log 0x00790400,0x006AB400 \
  --hit-cap 500 --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start,61:start,66:start,71:start \
  --hold-ms 150 >"$OUT/oracle.log" 2>&1 &
oracle_pid=$!

cd "$ROOT/build" || exit 2
common=(
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
  ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1
  ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a'
  PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1
  ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_FAMILY_EDGE=1 ROGUESQ_LOG_M5_FAMILY_STORE=1
  ROGUESQ_LOG_M5_STATIC_CALLS=1 ROGUESQ_LOG_M5_FIELD348_WRITER=1
  ROGUESQ_LOG_M5_FIELD348_MEMSET=1 ROGUESQ_LOG_M5_TASK_LIFETIME=1
  ROGUESQ_LOG_M5_STAGE_CALLS=1 ROGUESQ_LOG_M5_STAGE_BYTES=1
  ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_PCM_WRITER=1
  ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_ROUTE_PREPARE=1
  ROGUESQ_LOG_M5_ROUTE_HANDOFF=1 ROGUESQ_LOG_M5_DYNAMIC_CALLBACK=1
)
for pair in image:1 silent:0; do
  arm=${pair%%:*}
  audio=${pair##*:}
  env "${common[@]}" ROGUESQ_AUDIO_UCODE=$audio ./RogueSquadron64Recomp >"$OUT/$arm.log" 2>&1 &
  print $! >"$OUT/$arm.pid"
  sleep 2
done

for tick in {1..300}; do
  done_count=0
  for arm in silent image; do
    pid=$(<"$OUT/$arm.pid")
    if ! kill -0 "$pid" 2>/dev/null; then
      done_count=$((done_count+1))
    fi
  done
  (( done_count == 2 )) && break
  sleep 0.25
done
for arm in silent image; do
  pid=$(<"$OUT/$arm.pid")
  kill -KILL "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
done
kill -KILL "$oracle_pid" 2>/dev/null || true
wait "$oracle_pid" 2>/dev/null || true

for arm in silent image; do
  print -r -- "--- $arm ---" >>"$OUT/summary.txt"
  for marker in m5-family-store-control m5-family-store m5-family-edge-control m5-family-edge phase CRASH ABORT; do
    print -n "$marker=" >>"$OUT/summary.txt"
    grep -a -c "\[$marker\]" "$OUT/$arm.log" >>"$OUT/summary.txt" || print 0 >>"$OUT/summary.txt"
  done
done
for marker in 'positive-control' 'origin=0x00790400' 'origin=0x006ab400' 'watch write'; do
  print -n "$marker=" >>"$OUT/summary.txt"
  grep -a -c "$marker" "$OUT/oracle.log" >>"$OUT/summary.txt" || print 0 >>"$OUT/summary.txt"
done
