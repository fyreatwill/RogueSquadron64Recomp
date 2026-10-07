#!/bin/zsh
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s4086_m5_next_callsite"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"
OPID=""; GPID=""
trap '[[ -n "$GPID" ]] && kill -9 "$GPID" 2>/dev/null || true; [[ -n "$OPID" ]] && kill -9 "$OPID" 2>/dev/null || true' EXIT INT TERM
PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
cd "$ROOT" || exit 3

env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 60 \
  --watch-write 0x0:0x800000 \
  --watch-pc 0x8008D5FC,0x80084860,0x80084AB8,0x8008D604 \
  --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 \
  --hit-cap 500 --vi-trace --press "$PRESS" > "$OUT/oracle.log" 2>&1 &
OPID=$!
sleep 50
kill -9 "$OPID" 2>/dev/null || true
wait "$OPID" 2>/dev/null || true
if ! grep -aq 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log"; then
  print 'verdict=Hcoverage-oracle-control'; exit 0
fi
if ! grep -aq 'origin=0x006ab400 width=512' "$OUT/oracle.log"; then
  print 'verdict=Hcoverage-oracle-hangar'; exit 0
fi

cd "$ROOT/build" || exit 3
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a' \
  ROGUESQ_LOG_M5_AUDIO_CHANNEL_LOAD=1 ROGUESQ_LOG_M5_VOICE_MODULATION=1 \
  ./RogueSquadron64Recomp > "$OUT/port.log" 2>&1 &
GPID=$!
sleep 75
kill -9 "$GPID" 2>/dev/null || true
wait "$GPID" 2>/dev/null; PORT_RC=$?
control=1; hangar=1
call=$(grep -a -c '^\[m5-voice-callee\].*pc=0x8008D5FC' "$OUT/port.log" || true)
ret=$(grep -a -c '^\[m5-voice-mod-post\].*pc=0x8008D604' "$OUT/port.log" || true)
arith=$(grep -a -c '^\[m5-voice-mod-arith\].*pc=0x8008D610' "$OUT/port.log" || true)
call_hangar=$(grep -a '^\[m5-voice-callee\].*pc=0x8008D5FC' "$OUT/port.log" | grep -a -c 'origin=0x6AB400' || true)
ret_hangar=$(grep -a '^\[m5-voice-mod-post\].*pc=0x8008D604' "$OUT/port.log" | grep -a -c 'origin=0x6AB400' || true)
grep -a -E '^\[(phase|m5-voice-mod-(callee|post|arith|pre)|m5-audio-channel-load|CRASH|ABORT)' "$OUT/port.log" | tail -700 > "$OUT/port-summary.txt" || true
grep -a -E '^\[oracle\] (positive-control threshold|watch pc|exec-prev|done)|^\[vi\].*WIDTH (1024|512)' "$OUT/oracle.log" | tail -300 > "$OUT/oracle-summary.txt" || true
print "port_rc=$PORT_RC oracle_control=$control oracle_hangar=$hangar call=$call return=$ret arithmetic=$arith call_hangar=$call_hangar return_hangar=$ret_hangar" | tee "$OUT/driver.txt"
if (( call > 0 && ret > 0 && arith > 0 && call_hangar > 0 && ret_hangar > 0 )); then
  print 'verdict=qualified; compare retail watched PCs with port call/return/arithmetic rows' | tee -a "$OUT/driver.txt"
else
  print 'verdict=Hcoverage-port' | tee -a "$OUT/driver.txt"
fi
exit 0
