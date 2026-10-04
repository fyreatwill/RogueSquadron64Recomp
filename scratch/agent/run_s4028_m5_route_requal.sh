#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=${RS64_BOUNDARY_OUT:-$ROOT/scratch/agent/s4028_m5_route_requal}
BUILD=$ROOT/build
ORACLE=$ROOT/tools/oracle/build/rs64_oracle
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"

cleanup() {
  for pid in "${oracle_pid:-}" "${declared_pid:-}" "${silent_pid:-}" "${legacy_pid:-}"; do
    [[ -n "$pid" ]] && kill -KILL "$pid" 2>/dev/null || true
  done
}
trap cleanup EXIT INT TERM

env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 75 \
  --watch-write 0x0:0x800000 --hit-cap 10000 \
  --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 \
  --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > "$OUT/retail.log" 2>&1 & oracle_pid=$!

run_port() {
  local name="$1"; shift
  ( cd "$BUILD" && env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 \
    ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
    ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=110 \
    PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 ROGUESQ_LOG_PHASE=1 \
    ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_RSP_SOURCE=1 \
    ROGUESQ_LOG_M5_SCHEDULER_BOUNDARY=1 "$@" ./RogueSquadron64Recomp ) \
    > "$OUT/$name.log" 2>&1 & print $!
}

declared_pid=$(run_port declared-real ROGUESQ_AUDIO_UCODE=1)
silent_pid=$(run_port declared-silent ROGUESQ_AUDIO_UCODE=0)
legacy_pid=$(run_port legacy-real ROGUESQ_AUDIO_UCODE=1 ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1)
print "oracle=$oracle_pid declared=$declared_pid silent=$silent_pid legacy=$legacy_pid" > "$OUT/driver.log"

for _ in {1..480}; do
  alive=0
  for pid in "$oracle_pid" "$declared_pid" "$silent_pid" "$legacy_pid"; do
    kill -0 "$pid" 2>/dev/null && alive=1
  done
  (( alive )) || break
  sleep 0.25
done

for pid in "$oracle_pid" "$declared_pid" "$silent_pid" "$legacy_pid"; do
  kill -KILL "$pid" 2>/dev/null || true
done
for pid in "$oracle_pid" "$declared_pid" "$silent_pid" "$legacy_pid"; do
  wait "$pid" 2>/dev/null || true
done

for name in retail declared-real declared-silent legacy-real; do
  log="$OUT/$name.log"
  print -r -- "--- $name ---" >> "$OUT/driver.log"
  grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|m5-audio-stage|m5-scheduler-boundary|m5-rsp-source-hook-control|\[CRASH\]|\[ABORT\]|\[phase\]' "$log" | tail -260 >> "$OUT/driver.log" || true
done
