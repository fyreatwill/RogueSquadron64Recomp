#!/bin/zsh
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s4691_m5_a11_wait_boundary"
mkdir -p "$OUT"
PIDS=()
cleanup() { for p in $PIDS; do kill -KILL "$p" 2>/dev/null; done; }
trap cleanup EXIT INT TERM

(
  cd "$ROOT/build" || exit 2
  env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
    ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 \
    ROGUESQ_AUTOPILOT='40:start,44:start,48:start,52:start,56:a,60:a,64:start,68:a' \
    ROGUESQ_AUTOPILOT_STOP_WIDTH=0 PROBE_PHASE_WIDTH=1024 \
    PROBE_PHASE_TIMEOUT=110 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
    ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_WAIT_CONTRACT=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 \
    ./RogueSquadron64Recomp > "$OUT/port.log" 2>&1
) &
PIDS+=($!)

"$ROOT/tools/oracle/build/rs64_oracle" \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 120 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --vi-trace --watch-write 0x0:0x800000 \
  --watch-write 0x154620:0x1658a0 --watch-pc 0x8009B7A8,0x8009B7CC,0x8009B7EC \
  --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 \
  --first-watch 1 --pc-hist-watch 1 \
  --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 \
  --phase-origin-watch 1 > "$OUT/retail.log" 2>&1
echo $? > "$OUT/retail.rc"

for _ in {1..130}; do
  kill -0 "${PIDS[1]}" 2>/dev/null || break
  sleep 1
done
cleanup
wait 2>/dev/null
echo $? > "$OUT/port.rc"

{
  echo "port controls:"; grep -a -c 'vi_width=1024 .*origin=0x00790400' "$OUT/port.log" || true
  grep -a -c 'vi_width=512 .*origin=0x006AB400' "$OUT/port.log" || true
  echo "port wait:"; grep -a -c '\[s2076-wait-contract\]' "$OUT/port.log" || true
  grep -a -c 'edge=wait-entry' "$OUT/port.log" || true
  grep -a -c 'edge=wait-post-any-slot' "$OUT/port.log" || true
  grep -a -c 'waitforslot-guard-fire' "$OUT/port.log" || true
  echo "port writers:"; grep -a -c '\[s4471-b7cc\]' "$OUT/port.log" || true
  grep -a -c '0x8009B7EC' "$OUT/port.log" || true
  echo "retail controls:"; grep -a -c '\[watch\] write' "$OUT/retail.log" || true
  grep -a -c '\[vi\].*WIDTH 0 -> 320' "$OUT/retail.log" || true
  grep -a -c 'WIDTH 1024' "$OUT/retail.log" || true
  grep -a -c 'WIDTH 512.*0x006ab400' "$OUT/retail.log" || true
  echo "retail status/writers:"; grep -a -c '^\[hit\].*idx=1' "$OUT/retail.log" || true
  grep -a -c 'pc=0x8009b7a8\|pc=0x8009b7cc\|pc=0x8009b7ec' "$OUT/retail.log" || true
} > "$OUT/summary.txt"
