#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=$ROOT/scratch/agent/s4321_m5_mort_output
ORACLE=$ROOT/tools/oracle/build/rs64_oracle
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
REF=$ROOT/scratch/agent/s2138_mort/N64-Tools/N64SoundListToolUpdated/N64SoundLibrary/MORTDecoder.cpp

[[ "$OUT" != */.* ]] || exit 2
rm -rf "$OUT"
mkdir -p "$OUT"
cd "$ROOT" || exit 2

python3 tools/mort_probe.py --rom "$ROM" --speech-offset 0x583D90 \
  --speech-size 0x31D3E4 --indices 0,1,59,90 --reference "$REF" \
  > "$OUT/mort-reference.log" 2>&1 || exit 3

ORACLE_PRESS='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start'
PRESS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start'
COMMON=(ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_DESCRIPTOR=1 ROGUESQ_LOG_VI_CALLERS=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_FILTER_VOICE_AUDIT=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_ROUTE_TRANSITION=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' ROGUESQ_AUTOPILOT_STOP_WIDTH=512 M4_Y8000_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS="$PRESS")

env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 180 \
  --watch-write 0x0:0x800000 --watch-write 0xA0F50:0xA0F54 \
  --watch-write 0x141AD0:0x141AF0 --watch-write 0x1498A:0x1498B \
  --watch-pc 0x80029E80,0x80029F30 --vi-trace --press "$ORACLE_PRESS" \
  > "$OUT/oracle.log" 2>&1 &
OPID=$!
gate=0
for i in {1..130}; do
    if grep -a -q 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" && \
       grep -a -q 'origin=0x00790400 width=1024' "$OUT/oracle.log" && \
       grep -a -qi 'origin=0x006ab400' "$OUT/oracle.log"; then gate=1; break; fi
    kill -0 "$OPID" 2>/dev/null || break
    sleep 1
done
print "oracle_gate=$gate" > "$OUT/driver.log"
if (( gate == 0 )); then kill -9 "$OPID" 2>/dev/null; wait "$OPID" 2>/dev/null; exit 4; fi

launch() {
    local name=$1 arm=$2
    ( exec env "${COMMON[@]}" ROGUESQ_AUDIO_UCODE="$arm" zsh "$ROOT/tools/probe.sh" "$OUT/$name" 150 1 ) > "$OUT/$name-driver.log" 2>&1 &
    print "${name}_pid=$!" >> "$OUT/driver.log"
}
launch silent 0
launch image 1
sleep 165
for p in $(grep -E '_pid=' "$OUT/driver.log" | sed 's/.*=//') "$OPID"; do kill -9 "$p" 2>/dev/null || true; done
wait "$OPID" 2>/dev/null || true

for f in silent image; do
    log="$OUT/$f/run.log"
    print -- "--- $f ---" >> "$OUT/driver.log"
    for marker in '[phase]' '[m5-descriptor-start]' '[init-desc]' '[filter-voice-audit-control]' '[filter-voice-audit]' '[pcm-boundary-source]' '[pcm-boundary-consumer]' 'site=0x8009C540' 'site=0x8009C88C' 'site=0x8009D740' '[m5-port-vi-control]' '[m5-port-retail-target]' '[CRASH]' '[ABORT]'; do
        print "$marker=$(grep -a -F -c "$marker" "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    done
done
print -- "--- reference ---" >> "$OUT/driver.log"
grep -a -E '^\[(control|row|verdict|warning)\]' "$OUT/mort-reference.log" >> "$OUT/driver.log"
print -- "--- retail controls ---" >> "$OUT/driver.log"
grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|\[oracle\] done' "$OUT/oracle.log" | tail -20 >> "$OUT/driver.log"
