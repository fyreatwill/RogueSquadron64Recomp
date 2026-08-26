#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2325_m5_task_output_join}
OUT="$ROOT/scratch/agent/$TAG"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
ORACLE_CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ORACLE_ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
ORACLE_VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
WINCTL="$BUILD/winctl"
mkdir -p "$OUT"

if [[ ! -x "$ORACLE" || ! -f "$ORACLE_CORE" || ! -f "$ORACLE_ROM" || ! -f "$ORACLE_VIDEO" ]]; then
    print "ERROR: retail oracle prerequisites are missing" > "$OUT/driver.log"
    exit 2
fi
if [[ ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" || ! -x "$WINCTL" ]]; then
    print "ERROR: build/ control prerequisites are missing" > "$OUT/driver.log"
    exit 3
fi

cd "$ROOT" || exit 4

PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
PORT_PRESS=(6 11 16 21 26 31 36 41 46 51 56)
COMMON=(
    ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1
    ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
    ROGUESQ_M5_C88_VALUE=0 ROGUESQ_STUB_MISSING_FUNCS=1
    ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1
    ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1
    ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_M5_B40_ROUTE=1
    ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1
    ROGUESQ_LOG_FILTER_VOICE_AUDIT=1
)

print "oracle_start" > "$OUT/driver.log"
env "$ORACLE" \
    --core "$ORACLE_CORE" --rom "$ORACLE_ROM" --video "$ORACLE_VIDEO" \
    --secs 180 \
    --watch-write 0x0:0x800000 \
    --watch-write 0x166000:0x16A000 \
    --watch-write 0x141AD0:0x141AF0 \
    --watch-write 0xA0F50:0xA0F54 \
    --watch-write 0x1498A:0x1498C \
    --watch-write 0x154620:0x154624 \
    --hit-cap 200 --watch-pc 0x800078EC \
    --pc-phase-log-width 0x006AB400:512 \
    --pc-hist-phase 0x006AB400:512 --pc-hist-watch 2 \
    --post-value-watch 2 \
    --post-value-pc 0x8008EB8C,0x8008EBBC,0x80094648 \
    --vi-trace --press "$PRESS" > "$OUT/oracle.log" 2>&1
oracle_rc=$?

oracle_gate=0
if (( oracle_rc == 0 )) && \
   grep -a -q '^\[oracle\] watch write \[0x00000000,0x00800000): [1-9][0-9]* hit' "$OUT/oracle.log" && \
   grep -a -q '^\[oracle\] watch write \[0x00166000,0x0016a000): [1-9][0-9]* hit' "$OUT/oracle.log" && \
   grep -a -q '^\[oracle\] watch write \[0x00141ad0,0x00141af0): [1-9][0-9]* hit' "$OUT/oracle.log" && \
   grep -a -q '^\[oracle\] watch write \[0x000a0f50,0x000a0f54): [1-9][0-9]* hit' "$OUT/oracle.log" && \
   grep -a -q '^\[oracle\] watch write \[0x00154620,0x00154624): [1-9][0-9]* hit' "$OUT/oracle.log" && \
   grep -a -q '^\[oracle\] watch write \[0x0001498a,0x0001498c): 0 hit' "$OUT/oracle.log" && \
   grep -a -q '^\[vi\].*origin=0x00790400' "$OUT/oracle.log" && \
   grep -a -q '^\[vi\].*origin=0x006ab400' "$OUT/oracle.log" && \
   grep -a -q '^\[oracle\] writer-pc-phase origin=0x006ab400 width=512 watch=2 range=' "$OUT/oracle.log" && \
   grep -a -q '^\[oracle\] writer-pc pc=0x8008eb8c n=' "$OUT/oracle.log" && \
   grep -a -q '^\[oracle\] writer-pc pc=0x8008ebbc n=' "$OUT/oracle.log" && \
   grep -a -q '^\[oracle\] writer-pc pc=0x80094648 n=' "$OUT/oracle.log"; then
    oracle_gate=1
fi
print "oracle_rc=$oracle_rc oracle_controls=$oracle_gate" | tee -a "$OUT/driver.log"
grep -a -E '^\[oracle\] (done:|watch write \[0x00000000|watch write \[0x00166000|watch write \[0x00141ad0|watch write \[0x000a0f50|watch write \[0x0001498a|watch write \[0x00154620|writer-pc-phase|writer-pc pc=)' "$OUT/oracle.log" | tail -40 >> "$OUT/driver.log" || true
if (( oracle_gate == 0 )); then
    print "verdict=H-CoverageInvalid oracle_controls=0" | tee -a "$OUT/driver.log"
    exit 5
fi

GAME_PID=""
KEY_PID=""
cleanup_game() {
    local pid="$1"
    local keypid="$2"
    if [[ -n "$keypid" ]] && kill -0 "$keypid" 2>/dev/null; then kill -9 "$keypid" 2>/dev/null || true; fi
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        /usr/bin/pkill -KILL -P "$pid" 2>/dev/null || true
        kill -9 "$pid" 2>/dev/null || true
    fi
}
trap 'cleanup_game "$GAME_PID" "$KEY_PID"' EXIT INT TERM

raise_game() {
    local pid="$1"
    "$WINCTL" activate "$pid" >/dev/null 2>&1 || true
    /usr/bin/osascript -e "tell application \"System Events\" to set frontmost of first application process whose unix id is $pid to true" >/dev/null 2>&1 || true
}

wait_for_window() {
    local pid="$1"
    local deadline=$((SECONDS + 30))
    local wid=""
    while (( SECONDS < deadline )); do
        if ! kill -0 "$pid" 2>/dev/null; then return 1; fi
        wid="$($WINCTL find "$pid" 2>/dev/null || true)"
        if [[ -n "$wid" ]]; then
            print "window pid=$pid id=${wid%% *}" >> "$OUT/driver.log"
            return 0
        fi
        sleep 1
    done
    return 1
}

send_keys() {
    local name="$1"
    local pid="$2"
    local previous=0
    print "port_input=$name schedule=eleven-start keycode=36" >> "$OUT/driver.log"
    for at in $PORT_PRESS; do
        sleep "$((at - previous))"
        previous=$at
        if ! kill -0 "$pid" 2>/dev/null; then return 0; fi
        raise_game "$pid"
        "$WINCTL" key "$pid" 36 >/dev/null 2>&1 || true
        print "port_input=$name start_at_process_s=$at keycode=36" >> "$OUT/driver.log"
    done
}

run_arm() {
    local name="$1"
    local audio="$2"
    local log="$OUT/$name.log"
    if [[ "$audio" == 0 ]]; then
        ( cd "$BUILD" && exec env ${=COMMON} ROGUESQ_AUDIO_UCODE=0 ./RogueSquadron64Recomp ) > "$log" 2>&1 &
    else
        ( cd "$BUILD" && exec env ${=COMMON} ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp ) > "$log" 2>&1 &
    fi
    GAME_PID=$!
    print "${name}_pid=$GAME_PID" | tee -a "$OUT/driver.log"
    local window_ok=0
    wait_for_window "$GAME_PID" && window_ok=1
    if (( window_ok == 0 )); then
        print "${name}_window=missing" | tee -a "$OUT/driver.log"
    else
        send_keys "$name" "$GAME_PID" &
        KEY_PID=$!
    fi
    local hangar=0
    local deadline=$((SECONDS + 240))
    while (( SECONDS < deadline )); do
        if grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log"; then
            hangar=1
            print "${name}_hangar=observed; retaining_15s" | tee -a "$OUT/driver.log"
            sleep 15
            break
        fi
        if ! kill -0 "$GAME_PID" 2>/dev/null; then break; fi
        sleep 1
    done
    if (( hangar == 0 )); then print "${name}_hangar=missing" | tee -a "$OUT/driver.log"; fi
    cleanup_game "$GAME_PID" "$KEY_PID"
    wait "$KEY_PID" 2>/dev/null || true
    wait "$GAME_PID" 2>/dev/null
    local rc=$?
    print "${name}_rc=$rc ${name}_hangar=$hangar" | tee -a "$OUT/driver.log"
    GAME_PID=""
    KEY_PID=""
}

print "arms=stub_then_image; each uses eleven-start schedule" | tee -a "$OUT/driver.log"
run_arm stub 0
run_arm image 1

emit_counts() {
    local name="$1"
    local log="$OUT/$name.log"
    print -- "--- $name controls ---" >> "$OUT/driver.log"
    for marker in \
        '[audtask-dispatch]' '[audtask-abi]' '[audtask-dma-row]' '[audtask-dma-range]' \
        '[audtask-image-stage-row]' '[audtask-image-join]' '[audtask-join]' \
        '[audtask-join-range]' '[audio-return]' '[m5-gate]' '[slot-alloc]' \
        '[slot-sb]' '[init-desc]' '[filter-voice-audit]' '[pcm-boundary-source]' \
        '[pcm-boundary-consumer]' '[m5-b40-route]' '[m5-route-state]' '[CRASH]' '[ABORT]'; do
        print "$marker=$(grep -a -F -c "$marker" "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    done
    print "title=$(grep -a -c '^\[phase\] vi_width=1024 .*origin=0x00790400' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    print "hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
}
emit_counts stub
emit_counts image

awk '
function val(name,    i) {
    for (i = 1; i <= NF; i++) if (index($i, name "=") == 1) return substr($i, length(name) + 2)
    return ""
}
function hexnum(v,    i, d, n) {
    sub(/^0[xX]/, "", v); v=tolower(v); n=0
    for (i=1; i<=length(v); i++) { d=index("0123456789abcdef", substr(v,i,1))-1; if (d<0) return 0; n=n*16+d }
    return n
}
BEGIN { print "arm\tphase\twidth\torigin\tordinal\trow\tstage\tstage_event\tcomplete_event\tdest\tlen\tstage_fnv\tstage_nz\tclassification\tsource_event\tconsumer_event\tsource_nz\tconsumer_nz\tsource_before_consumer\tordering_violation" }
$1 == "[audtask-image-join]" {
    phase=val("phase")+0; width=val("width")+0; origin=val("origin")
    if (!((width==1024 && hexnum(origin)==7930880) || (width==512 && hexnum(origin)==6992896))) next
    print val("arm") "\t" phase "\t" width "\t" origin "\t" val("ordinal") "\t" val("row") "\t" val("stage") "\t" val("stage_event") "\t" val("complete_event") "\t" val("dest") "\t" val("len") "\t" val("stage_fnv") "\t" val("stage_nz") "\t" val("classification") "\t" val("source_event") "\t" val("consumer_event") "\t" val("source_nz") "\t" val("consumer_nz") "\t" val("source_before_consumer") "\t" val("ordering_violation")
}
' "$OUT/stub.log" "$OUT/image.log" > "$OUT/port-image-join.tsv"

awk '
function val(name,    i) { for (i=1;i<=NF;i++) if (index($i,name "=")==1) return substr($i,length(name)+2); return "" }
BEGIN { print "arm\tn\tphase\twidth\torigin\tbegin\tend\tdma_count\tsource_matches\tconsumer_matches\tcomplete\tdma_before_pcm\tsource_before_consumer\tpcm_after_task\tconsumer_after_task\tdmem_changed\tcanary_arm\tsource_n\tsource_nz\texit" }
$1 == "[audtask-join]" { print val("canary_arm") "\t" val("n") "\t" val("phase") "\t" val("width") "\t" val("origin") "\t" val("begin") "\t" val("end") "\t" val("dma_count") "\t" val("source_matches") "\t" val("consumer_matches") "\t" val("complete") "\t" val("dma_before_pcm") "\t" val("source_before_consumer") "\t" val("pcm_after_task") "\t" val("consumer_after_task") "\t" val("dmem_changed") "\t" val("canary_arm") "\t" val("source_n") "\t" val("source_nz") "\t" val("exit") }
' "$OUT/stub.log" "$OUT/image.log" > "$OUT/port-task-join.tsv"

awk '
function val(name,    i) { for (i=1;i<=NF;i++) if (index($i,name "=")==1) return substr($i,length(name)+2); return "" }
function hexnum(v,    i,d,n) { sub(/^0[xX]/,"",v); v=tolower(v); n=0; for (i=1;i<=length(v);i++) { d=index("0123456789abcdef",substr(v,i,1))-1; if (d<0) return 0; n=n*16+d } return n }
BEGIN { print "arm\tphase\twidth\torigin\tstage_rows\tnonzero_stage_rows\texact_source_consumer\tstage_only\trole" }
$1 == "[audtask-image-summary]" { print "image\t" val("phase") "\t" val("width") "\t" val("origin") "\t" val("stage_rows") "\t" val("nonzero_stage_rows") "\t" val("source_matches") "," val("consumer_matches") "\t" val("stage_only") "\timage-summary" }
$1 == "[audtask-image-join]" {
    if (val("width")+0 != 512 || hexnum(val("origin")) != 6992896) next
    if (val("stage_nz")+0 == 0) next
    d=val("dest"); stage[d]++; if (val("source_event")+0>0 && val("consumer_event")+0>0 && val("source_before_consumer")+0==1) exact[d]++
    if (val("classification")=="stage-only") only[d]++
}
END { for (d in stage) print "image\t*\t*\t*\t" stage[d] "\t*\t" (exact[d]+0) "\t" (only[d]+0) "\tby-destination dest=" d }
' "$OUT/image.log" > "$OUT/port-destination-summary.tsv"

awk '
function val(name,    i) { for (i=1;i<=NF;i++) if (index($i,name "=")==1) return substr($i,length(name)+2); return "" }
BEGIN { print "source\tkind\ttarget\tcaller\tphase\twidth\torigin\tordinal\trow\tactive\texit" }
$1 == "[m5-dispatch-boundary-control]" { print FILENAME "\tcontrol\t" val("target") "\t" val("caller") "\t" val("phase") "\t" val("width") "\t" val("origin") "\t*\t*\t" val("active") "\t*" }
$1 == "[m5-dispatch-boundary]" { print FILENAME "\ttarget\t" val("target") "\t" val("caller") "\t" val("phase") "\t" val("width") "\t" val("origin") "\t" val("ordinal") "\t" val("row") "\t" val("active") "\t" val("exit") }
' "$OUT/stub.log" "$OUT/image.log" > "$OUT/port-dispatch-boundary.tsv"

awk '
function val(name,    i) { for (i=1;i<=NF;i++) if (index($i,name "=")==1) return substr($i,length(name)+2); return "" }
BEGIN { print "pc\tcount" }
$1 == "[oracle]" && $2 == "writer-pc" && $3 ~ /^pc=/ { print val("pc") "\t" val("n") }
' "$OUT/oracle.log" > "$OUT/retail-task-output-writers.tsv"

image_stage_rows=$(grep -a -c '^\[audtask-image-join\]' "$OUT/image.log" 2>/dev/null || true)
image_nonzero=$(grep -a -E -c '^\[audtask-image-join\].*stage_nz=[1-9]' "$OUT/image.log" 2>/dev/null || true)
image_exact=$(grep -a -E -c '^\[audtask-image-join\].*stage_nz=[1-9].*source_event=[1-9][0-9]*.*consumer_event=[1-9][0-9]*.*source_before_consumer=1' "$OUT/image.log" 2>/dev/null || true)
image_only=$(grep -a -E -c '^\[audtask-image-join\].*stage_nz=[1-9].*classification=stage-only' "$OUT/image.log" 2>/dev/null || true)
dest_exact=$(awk -F '\t' '$9 ~ /by-destination/ && $7+0>0 {n++} END {print n+0}' "$OUT/port-destination-summary.tsv")
dest_only=$(awk -F '\t' '$9 ~ /by-destination/ && $8+0>0 {n++} END {print n+0}' "$OUT/port-destination-summary.tsv")
role_skew=0
if (( dest_exact > 0 && dest_only > 0 )); then role_skew=1; fi
print "table image_stage_rows=$image_stage_rows nonzero=$image_nonzero exact_source_consumer=$image_exact stage_only=$image_only destination_exact=$dest_exact destination_stage_only=$dest_only role_skew=$role_skew" | tee -a "$OUT/driver.log"

stub_hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/stub.log" 2>/dev/null || true)
image_hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/image.log" 2>/dev/null || true)
if (( oracle_gate == 0 || stub_hangar == 0 || image_hangar == 0 )); then
    verdict=H-CoverageInvalid
elif (( role_skew == 1 )); then
    verdict=H-Destination-Role-Skew
elif (( image_exact > 0 )); then
    verdict=H-Retail-Port-Shared-Output
elif (( image_nonzero > 0 )); then
    verdict=H-Port-Image-Stage-Only
else
    verdict=H-Port-Image-Stage-Only
fi
print "verdict=$verdict oracle_controls=$oracle_gate stub_hangar=$stub_hangar image_hangar=$image_hangar" | tee -a "$OUT/driver.log"
exit 0
