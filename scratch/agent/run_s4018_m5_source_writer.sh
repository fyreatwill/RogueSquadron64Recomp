#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=${RS64_BOUNDARY_OUT:-$ROOT/scratch/agent/s4018_m5_source_writer}
BUILD=$ROOT/build
ORACLE=$ROOT/tools/oracle/build/rs64_oracle
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"

if [[ ! -x "$ORACLE" || ! -f "$CORE" || ! -f "$ROM" || ! -f "$VIDEO" ||
      ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" ]]; then
  print -r -- setup_missing > "$OUT/driver.log"
  exit 2
fi

cleanup() {
  for pid in "${oracle_pid:-}" "${declared_pid:-}" "${legacy_pid:-}"; do
    [[ -n "$pid" ]] && kill -KILL "$pid" 2>/dev/null || true
  done
}
trap cleanup EXIT INT TERM

env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 75 \
  --watch-write 0x0:0x800000 --watch-write 0x1798B0:0x179A48 \
  --hit-cap 10000 --pc-hist-watch 1 \
  --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 \
  --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 \
  --pc-task-dump 0x80019CD8 --pc-task-type 2 --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > "$OUT/retail.log" 2>&1 & oracle_pid=$!

run_port() {
  local name="$1" legacy="$2"
  local extra=()
  [[ "$legacy" == 1 ]] && extra+=(ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1)
  ( cd "$BUILD" && env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 \
    ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
    ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=110 \
    PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 ROGUESQ_LOG_PHASE=1 \
    ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_RSP_SOURCE=1 \
    ROGUESQ_LOG_M5_SCHEDULER_BOUNDARY=1 ROGUESQ_AUDIO_UCODE=1 "${extra[@]}" \
    ./RogueSquadron64Recomp ) > "$OUT/$name.log" 2>&1 & print $!
}

declared_pid=$(run_port declared-real 0)
legacy_pid=$(run_port legacy-real 1)
print "oracle=$oracle_pid declared=$declared_pid legacy=$legacy_pid" > "$OUT/driver.log"
for _ in {1..480}; do
  alive=0
  for pid in "$oracle_pid" "$declared_pid" "$legacy_pid"; do
    kill -0 "$pid" 2>/dev/null && alive=1
  done
  (( alive )) || break
  sleep 0.25
done
for pid in "$oracle_pid" "$declared_pid" "$legacy_pid"; do kill -KILL "$pid" 2>/dev/null || true; done
for pid in "$oracle_pid" "$declared_pid" "$legacy_pid"; do wait "$pid" 2>/dev/null || true; done
for name in retail declared-real legacy-real; do
  log="$OUT/$name.log"
  print -r -- "--- $name ---" >> "$OUT/driver.log"
  grep -a -E 'positive-control threshold|pc-hist-phase|origin=0x00790400 width=1024|origin=0x006ab400 width=512|m5-audio-stage|m5-scheduler-boundary|m5-rsp-source-hook-control|\[CRASH\]|\[ABORT\]|\[phase\]' "$log" | tail -260 >> "$OUT/driver.log" || true
done
