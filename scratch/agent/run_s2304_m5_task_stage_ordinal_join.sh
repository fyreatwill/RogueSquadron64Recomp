#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s2304_m5_task_stage_ordinal_join"
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
RING_SPECS=(
    0x166450:0x166750 0x166750:0x166A50 0x166A50:0x166D50
    0x166D50:0x167050 0x167050:0x167350 0x167350:0x167650
    0x167650:0x167950 0x167950:0x167C50 0x167C50:0x167F50
    0x167F50:0x168250 0x168250:0x168550 0x168550:0x168850
    0x168850:0x168B50 0x168B50:0x168E50 0x168E50:0x169150
    0x169150:0x169450
)
COMMON=(
    ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
    ROGUESQ_SPIN_YIELD=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_STUB_MISSING_FUNCS=1
    ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1
    ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1
    ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1
    ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_FILTER_VOICE_AUDIT=1
)
ORACLE_ARGS=(
    --core "$ORACLE_CORE" --rom "$ORACLE_ROM" --video "$ORACLE_VIDEO" --secs 180
    --watch-write 0x0:0x800000 --watch-write 0x166000:0x16A000
    --watch-write 0x141AD0:0x141AF0
)
for spec in $RING_SPECS; do ORACLE_ARGS+=(--watch-write "$spec"); done
ORACLE_ARGS+=(
    --hit-cap 200 --watch-pc 0x800078EC --pc-phase-log-width 0x006AB400:512
    --pc-hist-phase 0x006AB400:512 --pc-hist-watch 2 --post-value-watch 2
    --post-value-pc 0x8008EB8C,0x8008EBBC,0x80094648 --vi-trace --press "$PRESS"
)

ORACLE_PID=""
PORT_PID=""
KEY_PID=""
cleanup() {
    for pid in "$KEY_PID" "$PORT_PID" "$ORACLE_PID"; do
        if [[ -n "$pid" && "$pid" != 0 ]] && kill -0 "$pid" 2>/dev/null; then
            /usr/bin/pkill -KILL -P "$pid" 2>/dev/null || true
            kill -9 "$pid" 2>/dev/null || true
        fi
    done
}
trap cleanup EXIT INT TERM

print "oracle_start" > "$OUT/driver.log"
env "$ORACLE" ${=ORACLE_ARGS} > "$OUT/oracle.log" 2>&1 &
ORACLE_PID=$!
print "oracle_pid=$ORACLE_PID" >> "$OUT/driver.log"
(
    cd "$BUILD" || exit 2
    exec env ${=COMMON} ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp
) > "$OUT/port.log" 2>&1 &
PORT_PID=$!
print "port_pid=$PORT_PID" | tee -a "$OUT/driver.log"

WID=""
window_deadline=$((SECONDS + 30))
while [[ -z "$WID" && $SECONDS -lt $window_deadline ]]; do
    if ! kill -0 "$PORT_PID" 2>/dev/null; then break; fi
    WID="$($WINCTL find "$PORT_PID" 2>/dev/null || true)"
    [[ -n "$WID" ]] || sleep 1
done
if [[ -z "$WID" ]]; then
    print "port_window=missing" | tee -a "$OUT/driver.log"
else
    print "port_window=${WID%% *}" >> "$OUT/driver.log"
    (
        previous=0
        for at in $PORT_PRESS; do
            sleep "$((at - previous))"
            previous=$at
            kill -0 "$PORT_PID" 2>/dev/null || exit 0
            "$WINCTL" activate "$PORT_PID" >/dev/null 2>&1 || true
            /usr/bin/osascript -e "tell application \"System Events\" to set frontmost of first application process whose unix id is $PORT_PID to true" >/dev/null 2>&1 || true
            "$WINCTL" key "$PORT_PID" 36 >/dev/null 2>&1 || true
            print "port_input=start process_s=$at keycode=36" >> "$OUT/driver.log"
        done
    ) &
    KEY_PID=$!
fi

oracle_gate=0
port_title=0
port_hangar=0
port_retained=0
deadline=$((SECONDS + 205))
while (( SECONDS < deadline )); do
    if (( oracle_gate == 0 )) && grep -a -q 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" && grep -a -q 'origin=0x00790400 width=1024' "$OUT/oracle.log" && grep -a -qi 'origin=0x006ab400 width=512' "$OUT/oracle.log"; then
        oracle_gate=1
        print "oracle_controls=passed whole_rdram=10000 title=1 hangar=1" | tee -a "$OUT/driver.log"
    fi
    if (( port_title == 0 )) && grep -a -q '^\[phase\] vi_width=1024 .*origin=0x00790400' "$OUT/port.log"; then
        port_title=1
        print "port_title=observed" | tee -a "$OUT/driver.log"
    fi
    if (( port_hangar == 0 )) && grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/port.log"; then
        port_hangar=1
        print "port_hangar=observed; retaining_15s" | tee -a "$OUT/driver.log"
        sleep 15
        if kill -0 "$PORT_PID" 2>/dev/null; then
            /usr/bin/pkill -KILL -P "$PORT_PID" 2>/dev/null || true
            kill -9 "$PORT_PID" 2>/dev/null || true
        fi
        port_retained=1
    fi
    if (( oracle_gate == 1 && port_hangar == 1 && port_retained == 1 )) && ! kill -0 "$ORACLE_PID" 2>/dev/null; then break; fi
    if ! kill -0 "$ORACLE_PID" 2>/dev/null && (( oracle_gate == 0 )); then break; fi
    if ! kill -0 "$PORT_PID" 2>/dev/null && (( port_hangar == 0 )); then break; fi
    sleep 1
done

for pid in "$KEY_PID" "$PORT_PID"; do
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        /usr/bin/pkill -KILL -P "$pid" 2>/dev/null || true
        kill -9 "$pid" 2>/dev/null || true
    fi
done
wait "$KEY_PID" 2>/dev/null || true
wait "$PORT_PID" 2>/dev/null
port_rc=$?
if kill -0 "$ORACLE_PID" 2>/dev/null; then
    oracle_deadline=$((SECONDS + 25))
    while kill -0 "$ORACLE_PID" 2>/dev/null && (( SECONDS < oracle_deadline )); do sleep 1; done
fi
if kill -0 "$ORACLE_PID" 2>/dev/null; then kill -9 "$ORACLE_PID" 2>/dev/null || true; fi
wait "$ORACLE_PID" 2>/dev/null
oracle_rc=$?
retail_writer=0
if grep -a -q '^\[oracle\] writer-pc-phase origin=0x006ab400 width=512 watch=2 range=' "$OUT/oracle.log" && grep -a -q '^\[oracle\] writer-pc pc=0x8008eb8c n=' "$OUT/oracle.log" && grep -a -q '^\[oracle\] writer-pc pc=0x8008ebbc n=' "$OUT/oracle.log" && grep -a -q '^\[oracle\] writer-pc pc=0x80094648 n=' "$OUT/oracle.log"; then
    retail_writer=1
fi
print "oracle_rc=$oracle_rc port_rc=$port_rc oracle_controls=$oracle_gate retail_writer=$retail_writer port_title=$port_title port_hangar=$port_hangar" >> "$OUT/driver.log"

awk '
function val(name,    i) {
    for (i = 1; i <= NF; i++) {
        if (index($i, name "=") == 1) return substr($i, length(name) + 2)
    }
    return ""
}
function norm(v) {
    sub(/^0[xX]/, "", v)
    return tolower(v)
}
function makekey(phase, width, origin, n) {
    return phase "|" width "|" norm(origin) "|" n
}
function exact_pcm(pk, dest, len, fnv, nz,    d) {
    d = norm(dest) "|" norm(len) "|" norm(fnv) "|" nz
    return (pcm_dest[pk] == d) ? 1 : 0
}
$1 == "[audtask-dma-row]" {
    k = makekey(val("phase"), val("width"), val("origin"), val("n"))
    current_dma_key = k
    task_fields[k] = "ucode=" val("ucode") ";ucode_size=" val("ucode_size") \
        ";ucode_data=" val("ucode_data") ";ucode_data_size=" val("ucode_data_size") \
        ";data_ptr=" val("data_ptr") ";data_size=" val("data_size") \
        ";output_buff=" val("output_buff") ";output_buff_size=" val("output_buff_size") \
        ";yield_ptr=" val("yield_ptr") ";yield_size=" val("yield_size")
    next
}
$1 == "[audtask-dma-range]" {
    k = current_dma_key
    i = ++dma_n[k]
    d = val("dram")
    sub(/\.\..*$/, "", d)
    dma_dest[k, i] = norm(d)
    dma_len[k, i] = norm(val("len"))
    dma_fnv[k, i] = norm(val("payload_fnv"))
    dma_nz[k, i] = val("payload_nz") + 0
    next
}
$1 == "[audio-join-pcm]" {
    pk = makekey(val("phase"), val("width"), val("origin"), val("n")) SUBSEP val("kind")
    pcm_event[pk] = val("event") + 0
    pcm_dest[pk] = norm(val("rdram")) "|" norm(val("bytes")) "|" norm(val("fnv")) "|" (val("nz") + 0)
    next
}
$1 == "[audtask-image-stage-row]" {
    if ((val("nz") + 0) == 0) next
    ++stage_n
    stage_key[stage_n] = makekey(val("phase"), val("width"), val("origin"), val("row"))
    stage_phase[stage_n] = val("phase")
    stage_width[stage_n] = val("width")
    stage_origin[stage_n] = norm(val("origin"))
    stage_task[stage_n] = val("row")
    stage_route[stage_n] = val("ordinal")
    stage_arm[stage_n] = val("arm")
    stage_stage[stage_n] = val("stage")
    stage_dest[stage_n] = norm(val("dest"))
    stage_len[stage_n] = norm(val("len"))
    stage_fnv[stage_n] = norm(val("fnv"))
    stage_nz[stage_n] = val("nz") + 0
    next
}
END {
    print "phase\twidth\torigin\ttask_ordinal\ttask_fields\tstage\tdest\tlen\tstage_fnv\tstage_nz\tdma_match\tpcm_source_match\tpcm_consumer_match\tsource_before_consumer\troute_ordinal\tarm"
    for (s = 1; s <= stage_n; s++) {
        k = stage_key[s]
        dm = 0
        for (i = 1; i <= dma_n[k]; i++) {
            if (dma_dest[k, i] == stage_dest[s] && dma_len[k, i] == stage_len[s] && dma_fnv[k, i] == stage_fnv[s] && dma_nz[k, i] == stage_nz[s]) dm = 1
        }
        sk = k SUBSEP "source"
        ck = k SUBSEP "consumer"
        sm = exact_pcm(sk, stage_dest[s], stage_len[s], stage_fnv[s], stage_nz[s])
        cm = exact_pcm(ck, stage_dest[s], stage_len[s], stage_fnv[s], stage_nz[s])
        before = (sm && cm) ? ((pcm_event[sk] < pcm_event[ck]) ? "yes" : "no") : "NA"
        fields = (k in task_fields) ? task_fields[k] : "MISSING"
        print stage_phase[s] "\t" stage_width[s] "\t0x" stage_origin[s] "\t" stage_task[s] "\t" fields "\t" stage_stage[s] "\t0x" stage_dest[s] "\t0x" stage_len[s] "\t" stage_fnv[s] "\t" stage_nz[s] "\t" dm "\t" sm "\t" cm "\t" before "\t" stage_route[s] "\t" stage_arm[s]
    }
}' "$OUT/port.log" > "$OUT/ordinal-table.tsv"

print -- "--- retail controls and target writers ---" >> "$OUT/driver.log"
grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|writer-pc-phase origin=0x006ab400 width=512 watch=2' "$OUT/oracle.log" | tail -80 >> "$OUT/driver.log" || true
print -- "--- port join table: $OUT/ordinal-table.tsv ---" >> "$OUT/driver.log"
sed -n '1,10000p' "$OUT/ordinal-table.tsv" >> "$OUT/driver.log"

table_rows=$(awk -F '\t' 'NR > 1 { n++ } END { print n + 0 }' "$OUT/ordinal-table.tsv")
dma_ok=$(awk -F '\t' 'NR > 1 && $11 == 1 { n++ } END { print n + 0 }' "$OUT/ordinal-table.tsv")
source_ok=$(awk -F '\t' 'NR > 1 && $12 == 1 { n++ } END { print n + 0 }' "$OUT/ordinal-table.tsv")
consumer_ok=$(awk -F '\t' 'NR > 1 && $13 == 1 { n++ } END { print n + 0 }' "$OUT/ordinal-table.tsv")
ordered_ok=$(awk -F '\t' 'NR > 1 && $14 == "yes" { n++ } END { print n + 0 }' "$OUT/ordinal-table.tsv")
bad_rows=$(awk -F '\t' 'NR > 1 && ($11 != 1 || $12 != 1 || $13 != 1 || $14 != "yes") { n++ } END { print n + 0 }' "$OUT/ordinal-table.tsv")
print "join_counts table_rows=$table_rows dma_ok=$dma_ok source_ok=$source_ok consumer_ok=$consumer_ok ordered_ok=$ordered_ok bad_rows=$bad_rows" | tee -a "$OUT/driver.log"

if (( oracle_gate == 0 || retail_writer == 0 || port_title == 0 || port_hangar == 0 || table_rows == 0 )); then
    print "verdict=H-CoverageInvalid" | tee -a "$OUT/driver.log"
elif (( bad_rows == 0 )); then
    print "verdict=H-TaskStageConsumerComplete" | tee -a "$OUT/driver.log"
else
    print "verdict=H-TaskStageOutputGap" | tee -a "$OUT/driver.log"
fi
exit 0
