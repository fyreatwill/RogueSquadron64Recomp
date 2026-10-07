#!/bin/zsh
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s4090_m5_callee_values"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"
OPID=""; GPID=""
trap '[[ -n "$GPID" ]] && kill -9 "$GPID" 2>/dev/null || true; [[ -n "$OPID" ]] && kill -9 "$OPID" 2>/dev/null || true' EXIT INT TERM
PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
cd "$ROOT" || exit 3
env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 120 \
  --watch-write 0x0:0x800000 --watch-pc 0x8008D5FC,0x80084860,0x8008488C,0x800848A8,0x800848C4,0x80084AB8 \
  --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 \
  --hit-cap 500 --vi-trace --press "$PRESS" > "$OUT/oracle.log" 2>&1 &
OPID=$!
sleep 50
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a' \
  ROGUESQ_LOG_M5_AUDIO_CHANNEL_LOAD=1 ROGUESQ_LOG_M5_VOICE_MODULATION=1 \
  "$ROOT/build/RogueSquadron64Recomp" > "$OUT/port.log" 2>&1 &
GPID=$!
sleep 75
kill -9 "$GPID" 2>/dev/null || true
wait "$GPID" 2>/dev/null; GRC=$?
kill -9 "$OPID" 2>/dev/null || true
wait "$OPID" 2>/dev/null || true
OPID=""
title=$(grep -a -c '^\[phase\].*vi_width=1024' "$OUT/port.log" || true)
hangar=$(grep -a -c '^\[phase\].*vi_width=512.*origin=0x006AB400' "$OUT/port.log" || true)
entry=$(grep -a -c '^\[m5-voice-callee\].*stage=entry' "$OUT/port.log" || true)
detail=$(grep -a -c '^\[m5-voice-callee-detail\]' "$OUT/port.log" || true)
ret=$(grep -a -c '^\[m5-voice-callee\].*stage=return' "$OUT/port.log" || true)
post=$(grep -a -c '^\[m5-voice-mod-post\].*pc=0x8008D604' "$OUT/port.log" || true)
grep -aE '^\[(phase|m5-voice-callee|m5-voice-callee-detail|m5-voice-mod-post|CRASH|ABORT)' "$OUT/port.log" | tail -500 > "$OUT/port-summary.txt" || true
oracle_control=$(grep -a -c 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" || true)
print "port_rc=$GRC oracle_control=$oracle_control title=$title hangar=$hangar entry=$entry detail=$detail return=$ret post=$post" | tee "$OUT/driver.log"
if (( title > 0 && hangar > 0 && oracle_control > 0 && entry > 0 && detail > 0 && ret > 0 && post > 0 )); then
  print 'verdict=qualified; compare phase-scoped retail and port detail rows' | tee -a "$OUT/driver.log"
else
  print 'verdict=Hcoverage' | tee -a "$OUT/driver.log"
fi
exit 0
