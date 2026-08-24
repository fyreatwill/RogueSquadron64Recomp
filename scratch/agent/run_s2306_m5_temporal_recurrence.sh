#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s2306_m5_temporal_recurrence"
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
        print "port_hangar=observed; retaining_45s" | tee -a "$OUT/driver.log"
        sleep 45
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

awk -v window_file="$OUT/window-table.tsv" -v summary_file="$OUT/destination-summary.tsv" '
function val(name,    i) {
    for (i = 1; i <= NF; i++) if (index($i, name "=") == 1) return substr($i, length(name) + 2)
    return ""
}
function norm(v) { sub(/^0[xX]/, "", v); return tolower(v) }
function hexnum(v,    s,i,c,n,d) {
    s=norm(v); n=0
    for (i=1; i<=length(s); i++) {
        c=substr(s,i,1); d=index("0123456789abcdef",c)-1
        if (d < 0) return -1
        n=n*16+d
    }
    return n
}
function phys_guest(v,    s) {
    s=norm(v)
    if (length(s) == 8 && substr(s,1,2) == "80") s=substr(s,3)
    return s
}
function scope(phase,width,origin) { return phase "|" width "|" norm(origin) }
function scope_phase(sc,    a) { split(sc,a,"|"); return a[1] }
function scope_width(sc,    a) { split(sc,a,"|"); return a[2] }
function scope_origin(sc,    a) { split(sc,a,"|"); return a[3] }
function stage_tuple(dest,len,fnv,nz) { return hexnum(dest) "|" hexnum(len) "|" hexnum(fnv) "|" (nz+0) }
function make_pcm_tuple(guest,bytes,fnv,nz) { return hexnum(phys_guest(guest)) "|" (bytes+0) "|" hexnum(fnv) "|" (nz+0) }
function abs(v) { return v < 0 ? -v : v }
BEGIN {
    print "dest\tstage_rows\tdma_exact\tsource_exact\tconsumer_exact\tsource_payload_mismatch\tconsumer_payload_mismatch\tstage_only_rows" > summary_file
}
$1 == "[audtask-dma-row]" {
    current_key=scope(val("phase"),val("width"),val("origin")) "|" (val("n")+0)
    next
}
$1 == "[audtask-dma-range]" {
    i=++dma_n[current_key]
    d=val("dram"); sub(/\.\..*$/, "", d)
    dma_tuple[current_key,i]=stage_tuple(d,val("len"),val("payload_fnv"),val("payload_nz"))
    dma_event[current_key,i]=val("event")+0
    next
}
$1 == "[audio-join-pcm]" {
    k=scope(val("phase"),val("width"),val("origin")); kind=val("kind")
    i=++pcm_n[k,kind]
    pcm_ord[k,kind,i]=val("n")+0
    pcm_event[k,kind,i]=val("event")+0
    pcm_dest[k,kind,i]=hexnum(phys_guest(val("guest")))
    pcm_key[k,kind,i]=make_pcm_tuple(val("guest"),val("bytes"),val("fnv"),val("nz"))
    next
}
$1 == "[audtask-image-stage-row]" {
    if ((val("nz")+0)==0) next
    ++stage_n
    stage_scope[stage_n]=scope(val("phase"),val("width"),val("origin"))
    stage_task[stage_n]=val("row")+0
    stage_event[stage_n]=val("event")+0
    stage_kind[stage_n]=val("stage")+0
    stage_dest[stage_n]=val("dest")
    stage_len[stage_n]=val("len")
    stage_fnv[stage_n]=val("fnv")
    stage_nz[stage_n]=val("nz")+0
    next
}
END {
    print "phase\twidth\torigin\ttask_ordinal\tstage_event\tdma_event\tstage\tdest\tlen\tstage_fnv\tstage_nz\tsource_n\tconsumer_n\tsource_event\tconsumer_event\tsource_delta\tconsumer_delta\tdma_before_source\tsource_before_consumer"
    print "phase\twidth\torigin\ttask_ordinal\tstage\tstage_tuple\twithin_source_n\twithin_consumer_n\tany_source_n\tany_consumer_n\tany_source_delta\tany_consumer_delta" > window_file
    for (s=1; s<=stage_n; s++) {
        sc=stage_scope[s]; task=stage_task[s]; st=stage_tuple(stage_dest[s],stage_len[s],stage_fnv[s],stage_nz[s])
        dest_num=hexnum(phys_guest(stage_dest[s])); dest_key="0x" norm(phys_guest(stage_dest[s])); pcm_st=stage_tuple(phys_guest(stage_dest[s]),stage_len[s],stage_fnv[s],stage_nz[s])
        ++sum_rows[dest_key]
        key=sc "|" task; de="NA"
        for (i=1; i<=dma_n[key]; i++) if (dma_tuple[key,i]==st) de=dma_event[key,i]
        src_n="NA"; con_n="NA"; src_e="NA"; con_e="NA"; src_d="NA"; con_d="NA"
        any_src_n="NA"; any_con_n="NA"; any_src_d="NA"; any_con_d="NA"
        src_mismatch=0; con_mismatch=0
        best=999999; any_best=999999
        for (i=1; i<=pcm_n[sc,"source"]; i++) {
            if (pcm_dest[sc,"source",i]==dest_num && pcm_key[sc,"source",i]!=pcm_st) src_mismatch=1
            if (pcm_key[sc,"source",i]==pcm_st) {
            d=pcm_ord[sc,"source",i]-task
            if (abs(d)<any_best) { any_best=abs(d); any_src_n=pcm_ord[sc,"source",i]; any_src_d=d }
            if (abs(d)<=64 && (abs(d)<best || (abs(d)==best && pcm_event[sc,"source",i]<src_e))) { best=abs(d); src_n=pcm_ord[sc,"source",i]; src_d=d; src_e=pcm_event[sc,"source",i] }
            }
        }
        best=999999; any_best=999999
        for (i=1; i<=pcm_n[sc,"consumer"]; i++) {
            if (pcm_dest[sc,"consumer",i]==dest_num && pcm_key[sc,"consumer",i]!=pcm_st) con_mismatch=1
            if (pcm_key[sc,"consumer",i]==pcm_st) {
            d=pcm_ord[sc,"consumer",i]-task
            if (abs(d)<any_best) { any_best=abs(d); any_con_n=pcm_ord[sc,"consumer",i]; any_con_d=d }
            if (abs(d)<=64 && (abs(d)<best || (abs(d)==best && pcm_event[sc,"consumer",i]<con_e))) { best=abs(d); con_n=pcm_ord[sc,"consumer",i]; con_d=d; con_e=pcm_event[sc,"consumer",i] }
            }
        }
        if (de!="NA") ++sum_dma[dest_key]
        if (src_n!="NA") ++sum_src_exact[dest_key]
        if (con_n!="NA") ++sum_con_exact[dest_key]
        if (src_mismatch) ++sum_src_mismatch[dest_key]
        if (con_mismatch) ++sum_con_mismatch[dest_key]
        if (src_n=="NA" && con_n=="NA") ++sum_stage_only[dest_key]
        dbs=(src_e!="NA" && de!="NA") ? (de<src_e ? "yes" : "no") : "NA"
        sbc=(src_e!="NA" && con_e!="NA") ? (src_e<con_e ? "yes" : "no") : "NA"
        print scope_phase(sc) "\t" scope_width(sc) "\t0x" scope_origin(sc) "\t" task "\t" stage_event[s] "\t" de "\t" stage_kind[s] "\t0x" norm(stage_dest[s]) "\t0x" norm(stage_len[s]) "\t" norm(stage_fnv[s]) "\t" stage_nz[s] "\t" src_n "\t" con_n "\t" src_e "\t" con_e "\t" src_d "\t" con_d "\t" dbs "\t" sbc
        print scope_phase(sc) "\t" scope_width(sc) "\t0x" scope_origin(sc) "\t" task "\t" stage_kind[s] "\t" st "\t" src_n "\t" con_n "\t" any_src_n "\t" any_con_n "\t" any_src_d "\t" any_con_d >> window_file
    }
    for (dest in sum_rows) print dest "\t" sum_rows[dest]+0 "\t" sum_dma[dest]+0 "\t" sum_src_exact[dest]+0 "\t" sum_con_exact[dest]+0 "\t" sum_src_mismatch[dest]+0 "\t" sum_con_mismatch[dest]+0 "\t" sum_stage_only[dest]+0 >> summary_file
}' "$OUT/port.log" > "$OUT/temporal-table.tsv"

print -- "--- retail controls and target writers ---" >> "$OUT/driver.log"
grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|writer-pc-phase origin=0x006ab400 width=512 watch=2|writer-pc pc=' "$OUT/oracle.log" | tail -80 >> "$OUT/driver.log" || true
print -- "--- temporal table: $OUT/temporal-table.tsv ---" >> "$OUT/driver.log"
sed -n '1,10000p' "$OUT/temporal-table.tsv" >> "$OUT/driver.log"
print -- "--- window table: $OUT/window-table.tsv ---" >> "$OUT/driver.log"
sed -n '1,10000p' "$OUT/window-table.tsv" >> "$OUT/driver.log"
print -- "--- destination summary: $OUT/destination-summary.tsv ---" >> "$OUT/driver.log"
sed -n '1,10000p' "$OUT/destination-summary.tsv" >> "$OUT/driver.log"

table_rows=$(awk -F '\t' 'NR>1 {n++} END{print n+0}' "$OUT/temporal-table.tsv")
dma_ok=$(awk -F '\t' 'NR>1 && $6!="NA" {n++} END{print n+0}' "$OUT/temporal-table.tsv")
source_ok=$(awk -F '\t' 'NR>1 && $12!="NA" {n++} END{print n+0}' "$OUT/temporal-table.tsv")
consumer_ok=$(awk -F '\t' 'NR>1 && $13!="NA" {n++} END{print n+0}' "$OUT/temporal-table.tsv")
ordered_ok=$(awk -F '\t' 'NR>1 && $18=="yes" && $19=="yes" {n++} END{print n+0}' "$OUT/temporal-table.tsv")
outside_rows=$(awk -F '\t' 'NR>1 && (($7=="NA" && $9!="NA") || ($8=="NA" && $10!="NA")) {n++} END{print n+0}' "$OUT/window-table.tsv")
summary_mismatches=$(awk -F '\t' 'NR>1 {n += $6 + $7} END{print n+0}' "$OUT/destination-summary.tsv")
print "temporal_counts table_rows=$table_rows dma_ok=$dma_ok source_ok=$source_ok consumer_ok=$consumer_ok ordered_ok=$ordered_ok outside_rows=$outside_rows destination_payload_mismatches=$summary_mismatches" | tee -a "$OUT/driver.log"

if (( oracle_gate == 0 || retail_writer == 0 || port_title == 0 || port_hangar == 0 || table_rows == 0 )); then
    print "verdict=H-CoverageInvalid" | tee -a "$OUT/driver.log"
elif (( outside_rows > 0 )); then
    print "verdict=H-OrdinalWindowTooNarrow" | tee -a "$OUT/driver.log"
elif (( table_rows == ordered_ok )); then
    print "verdict=H-DelayedPCMPublication" | tee -a "$OUT/driver.log"
else
    print "verdict=H-StageUnconsumed" | tee -a "$OUT/driver.log"
fi
exit 0
