#!/bin/zsh
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s4081_m5_setup_witness"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"
cd "$ROOT" || exit 3
PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
OPID=""; GAMEPID=""
trap '[[ -n "$GAMEPID" ]] && kill -9 "$GAMEPID" 2>/dev/null || true; [[ -n "$OPID" ]] && kill -9 "$OPID" 2>/dev/null || true' EXIT INT TERM

cd "$ROOT/build" || exit 3
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a' \
  ROGUESQ_LOG_M5_AUDIO_CHANNEL_LOAD=1 ROGUESQ_LOG_M5_VOICE_MODULATION=1 \
  ROGUESQ_LOG_ALL=1 \
  ./RogueSquadron64Recomp > "$OUT/port.log" 2>&1 &
GAMEPID=$!
sleep 7
env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 180 \
  --watch-write 0x0:0x800000 \
  --watch-pc 0x800923E4 --pc-phase-log-width 0x00790400:1024 \
  --pc-phase-log-width 0x006AB400:512 --hit-cap 200 --vi-trace \
  --press "$PRESS" > "$OUT/oracle.log" 2>&1 &
OPID=$!
sleep 75
kill -9 "$GAMEPID" 2>/dev/null || true
wait "$GAMEPID" 2>/dev/null; print "port_rc=$?" | tee "$OUT/driver.log"
kill -9 "$OPID" 2>/dev/null || true
wait "$OPID" 2>/dev/null || true

grep -a -E '^\[oracle\] (positive-control threshold|watch pc|exec-prev|done)|^\[vi\].*WIDTH (1024|512)' "$OUT/oracle.log" | tail -160 > "$OUT/oracle-summary.txt" || true
grep -a -E '^\[(phase|m5-audio-channel-load|m5-voice-mod-call|m5-voice-mod-setup|m5-voice-mod-state|CRASH|ABORT)' "$OUT/port.log" | tail -400 > "$OUT/port-summary.txt" || true
control=0
grep -aq 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" && control=1
title=0; hangar=0
grep -aq 'origin=0x00790400 width=1024' "$OUT/oracle.log" && title=1
grep -aq 'origin=0x006ab400 width=512' "$OUT/oracle.log" && hangar=1
port_load=$(grep -a -c '^\[m5-audio-channel-load\]' "$OUT/port.log" || true)
port_call=$(grep -a -c '^\[m5-voice-mod-call\]' "$OUT/port.log" || true)
port_setup=$(grep -a -c '^\[m5-voice-mod-setup\]' "$OUT/port.log" || true)
port_state=$(grep -a -c '^\[m5-voice-mod-state\]' "$OUT/port.log" || true)
port_hangar_setup=$(grep -a -c '^\[m5-voice-mod-setup\].*origin=0x6AB400' "$OUT/port.log" || true)
port_hangar_call=$(grep -a -c '^\[m5-voice-mod-call\].*origin=0x6AB400' "$OUT/port.log" || true)
print "controls=$control title=$title hangar=$hangar port_load=$port_load port_setup=$port_setup port_call=$port_call port_state=$port_state port_hangar_setup=$port_hangar_setup port_hangar_call=$port_hangar_call" | tee -a "$OUT/driver.log"
if (( control && title && hangar && port_load > 0 && port_hangar_setup > 0 && port_hangar_call > 0 )); then
  print 'verdict=qualified; inspect setup registers and call inputs' | tee -a "$OUT/driver.log"
else
  print 'verdict=Hcoverage' | tee -a "$OUT/driver.log"
fi
exit 0
