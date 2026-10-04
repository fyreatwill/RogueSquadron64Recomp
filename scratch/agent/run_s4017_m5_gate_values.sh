#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=${RS64_BOUNDARY_OUT:-$ROOT/scratch/agent/s4017_m5_gate_values}
BUILD=$ROOT/build
ORACLE=$ROOT/tools/oracle/build/rs64_oracle
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"
cleanup() { for pid in "${oracle_pid:-}" "${declared_pid:-}" "${legacy_pid:-}"; do [[ -n "$pid" ]] && kill -KILL "$pid" 2>/dev/null || true; done; }
trap cleanup EXIT INT TERM
env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 75 \
  --watch-write 0xA0F50:0xA0F54 --watch-write 0x0:0x800000 \
  --watch-write 0x1798B0:0x179A48 --watch-pc 0x80094648 \
  --detail-watch 0 \
  --store-field-dump 0:0x8008EA34,0x8008EB40,0x8008ED48,0x8008EB7C,0x8008EC88 \
  --store-field-dump-any-phase \
  --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 \
  --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > "$OUT/retail.log" 2>&1 & oracle_pid=$!
run_port() {
  local name="$1" legacy="$2"; local extra=(); [[ "$legacy" == 1 ]] && extra+=(ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1)
  ( cd "$BUILD" && env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
    ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
    ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=110 PROBE_KEYS_FROM_PHASE=1 \
    PROBE_LEAVE_OK=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_M5_WRITER_ENTRY=1 \
    ROGUESQ_LOG_M5_CHANNEL_STORE=1 ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 \
    ROGUESQ_AUDIO_UCODE=1 "${extra[@]}" ./RogueSquadron64Recomp ) > "$OUT/$name.log" 2>&1 & print $!
}
declared_pid=$(run_port declared-real 0); legacy_pid=$(run_port legacy-real 1)
print "oracle=$oracle_pid declared=$declared_pid legacy=$legacy_pid" > "$OUT/driver.log"
for _ in {1..480}; do alive=0; for pid in "$oracle_pid" "$declared_pid" "$legacy_pid"; do kill -0 "$pid" 2>/dev/null && alive=1; done; (( alive )) || break; sleep 0.25; done
for pid in "$oracle_pid" "$declared_pid" "$legacy_pid"; do kill -KILL "$pid" 2>/dev/null || true; done
for pid in "$oracle_pid" "$declared_pid" "$legacy_pid"; do wait "$pid" 2>/dev/null || true; done
for name in retail declared-real legacy-real; do
  print -r -- "--- $name ---" >> "$OUT/driver.log"
  rg -a -e 'positive-control threshold' -e 'origin=0x00790400 width=1024' -e 'origin=0x006ab400 width=512' -e 'm5-gate' -e 'm5-writer' -e 'm5-rsp-source-hook-control' -e '\[CRASH\]' -e '\[ABORT\]' -e '\[phase\]' "$OUT/$name.log" | tail -240 >> "$OUT/driver.log" || true
done
