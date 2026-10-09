#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=$ROOT/scratch/agent/s4320_m5_callsite_trace
BUILD=$ROOT/build
ORACLE=$ROOT/tools/oracle/build/rs64_oracle
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start

mkdir -p "$OUT"
cd "$ROOT" || exit 2
COMMON=(ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_DESCRIPTOR=1 ROGUESQ_LOG_VI_CALLERS=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_FILTER_VOICE_AUDIT=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_ROUTE_TRANSITION=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS="$PRESS")

env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 180 --watch-write 0x0:0x800000 --watch-write 0xA0F50:0xA0F54 --watch-write 0x141AD0:0x141AF0 --watch-write 0x1498A:0x1498B --watch-pc 0x80029E80,0x80029F30 --vi-trace --press "$PRESS" > "$OUT/oracle.log" 2>&1 &
OPID=$!
gate=0
for i in {1..130}; do
    if grep -a -q 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" && grep -a -q 'origin=0x00790400 width=1024' "$OUT/oracle.log" && grep -a -qi 'origin=0x006ab400' "$OUT/oracle.log"; then gate=1; break; fi
    kill -0 "$OPID" 2>/dev/null || break
    sleep 1
done
print "oracle_gate=$gate" > "$OUT/driver.log"
if (( gate == 0 )); then kill -9 "$OPID" 2>/dev/null; wait "$OPID" 2>/dev/null; exit 5; fi

launch() {
    local name=$1 arm=$2
    ( exec env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE="$arm" zsh "$ROOT/tools/probe.sh" "$OUT/$name" 90 1 ) > "$OUT/$name-driver.log" 2>&1 &
    print "${name}_pid=$!" >> "$OUT/driver.log"
}
launch silent 0
launch image 1
sleep 105
for p in $(grep -E '_pid=' "$OUT/driver.log" | sed 's/.*=//') "$OPID"; do kill -9 "$p" 2>/dev/null || true; done
wait "$OPID" 2>/dev/null || true
for f in silent image; do
    log="$OUT/$f/run.log"
    print -- "--- $f ---" >> "$OUT/driver.log"
    for marker in '[phase]' '[m5-descriptor-start]' '[init-desc]' '[filter-voice-audit-control]' '[filter-voice-audit]' 'site=0x8009C540' 'site=0x8009C88C' 'site=0x8009D740' '[m5-port-vi-control]' '[m5-port-retail-target]' '[CRASH]' '[ABORT]'; do print "$marker=$(grep -a -F -c "$marker" "$log" 2>/dev/null || true)" >> "$OUT/driver.log"; done
done
print -- "--- retail controls ---" >> "$OUT/driver.log"
grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|\[oracle\] done' "$OUT/oracle.log" | tail -20 >> "$OUT/driver.log"
