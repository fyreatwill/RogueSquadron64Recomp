#!/bin/zsh
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s4091_m5_post_callee"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"
OPID=""; GPID=""
trap '[[ -n "$GPID" ]] && kill -9 "$GPID" 2>/dev/null || true; [[ -n "$OPID" ]] && kill -9 "$OPID" 2>/dev/null || true' EXIT INT TERM
PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
cd "$ROOT" || exit 3

env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 180 \
  --watch-write 0x0:0x800000 \
  --watch-pc 0x8008D5FC,0x80084860,0x8008488C,0x800848A8,0x800848C4,0x80084AB8 \
  --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 \
  --hit-cap 500 --vi-trace --press "$PRESS" > "$OUT/oracle.log" 2>&1 &
OPID=$!
sleep 150
oracle_control=$(grep -ai -c 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" || true)
oracle_title=$(grep -ai -c 'width=1024 origin=0x00790400' "$OUT/oracle.log" || true)
oracle_hangar=$(grep -ai -c 'width=512 origin=0x006AB400' "$OUT/oracle.log" || true)
if (( oracle_control == 0 || oracle_title == 0 || oracle_hangar == 0 )); then
  print "verdict=Hcoverage-oracle control=$oracle_control title=$oracle_title hangar=$oracle_hangar" | tee "$OUT/driver.log"
  exit 0
fi
kill -9 "$OPID" 2>/dev/null || true
wait "$OPID" 2>/dev/null || true
OPID=""

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
title=$(grep -a -c '^\[phase\].*vi_width=1024' "$OUT/port.log" || true)
hangar=$(grep -a -c '^\[phase\].*vi_width=512.*origin=0x006AB400' "$OUT/port.log" || true)
detail=$(grep -a -c '^\[m5-voice-callee-detail\]' "$OUT/port.log" || true)
post=$(grep -a -c '^\[m5-voice-callee\].*stage=return.*pc=0x80084860' "$OUT/port.log" || true)
grep -aE '^\[(phase|m5-voice-callee|m5-voice-callee-detail|m5-voice-mod-post|CRASH|ABORT)' "$OUT/port.log" | tail -500 > "$OUT/port-summary.txt" || true
print "port_rc=$PORT_RC oracle_control=$oracle_control oracle_title=$oracle_title oracle_hangar=$oracle_hangar title=$title hangar=$hangar detail=$detail post=$post" | tee "$OUT/driver.log"
if (( title > 0 && hangar > 0 && detail > 0 && post > 0 )); then
  print 'verdict=qualified; compare retail 0x80084AB8 rows with port stage=return v0 rows' | tee -a "$OUT/driver.log"
else
  print 'verdict=Hcoverage-port' | tee -a "$OUT/driver.log"
fi
exit 0
