#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
OUT="$ROOT/scratch/agent/s2309_m5_dynamic_zero_fill"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
ORACLE_CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ORACLE_ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
ORACLE_VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
WINCTL="$BUILD/winctl"
mkdir -p "$OUT"

if [[ ! -x "$ORACLE" || ! -f "$ORACLE_CORE" || ! -f "$ORACLE_ROM" || ! -f "$ORACLE_VIDEO" ]]; then
    print "ERROR: oracle prerequisites missing" > "$OUT/driver.log"
    exit 2
fi
if [[ ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" || ! -x "$WINCTL" ]]; then
    print "ERROR: port prerequisites missing" > "$OUT/driver.log"
    exit 3
fi
cd "$ROOT" || exit 4

PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
PORT_PRESS=(6 16 26 36 46 56)
COMMON=(
    ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
    ROGUESQ_SPIN_YIELD=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_STUB_MISSING_FUNCS=1
    ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1
    ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1
    ROGUESQ_LOG_M5_PCM_WRITER=1 ROGUESQ_LOG_M5_B40_ROUTE=1
    ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1
)
ORACLE_ARGS=(
    --core "$ORACLE_CORE" --rom "$ORACLE_ROM" --video "$ORACLE_VIDEO" --secs 180
    --watch-write 0x0:0x800000 --watch-write 0x166450:0x169450
    --watch-write 0x141AD0:0x141AF0 --hit-cap 200
    --watch-pc 0x800078EC --pc-phase-log-width 0x006AB400:512
    --pc-hist-phase 0x006AB400:512 --pc-hist-watch 1 --post-value-watch 1
    --post-value-pc 0x800078EC --vi-trace --press "$PRESS"
)

ORACLE_PID=0
PORT_PID=0
KEY_PID=0
kill_tree() {
    local pid="$1"
    if [[ "$pid" != 0 ]] && kill -0 "$pid" 2>/dev/null; then
        /usr/bin/pkill -KILL -P "$pid" 2>/dev/null || true
        kill -9 "$pid" 2>/dev/null || true
    fi
}
trap 'kill_tree "$KEY_PID"; kill_tree "$PORT_PID"; kill_tree "$ORACLE_PID"' EXIT INT TERM

print "oracle_start" > "$OUT/driver.log"
env "$ORACLE" $ORACLE_ARGS > "$OUT/oracle.log" 2>&1 &
ORACLE_PID=$!
(
    cd "$BUILD" || exit 2
    exec env $COMMON ./RogueSquadron64Recomp
) > "$OUT/port.log" 2>&1 &
PORT_PID=$!
print "oracle_pid=$ORACLE_PID port_pid=$PORT_PID" | tee -a "$OUT/driver.log"

window=""
until [[ -n "$window" || $SECONDS -ge 30 ]]; do
    kill -0 "$PORT_PID" 2>/dev/null || break
    window="$($WINCTL find "$PORT_PID" 2>/dev/null || true)"
    [[ -n "$window" ]] || sleep 1
done
if [[ -n "$window" ]]; then
    (
        previous=0
        for at in $PORT_PRESS; do
            sleep "$((at - previous))"
            previous=$at
            kill -0 "$PORT_PID" 2>/dev/null || exit 0
            "$WINCTL" activate "$PORT_PID" >/dev/null 2>&1 || true
            /usr/bin/osascript -e "tell application \"System Events\" to set frontmost of first application process whose unix id is $PORT_PID to true" >/dev/null 2>&1 || true
            "$WINCTL" key "$PORT_PID" 36 >/dev/null 2>&1 || true
        done
    ) &
    KEY_PID=$!
else
    print "port_window=missing" | tee -a "$OUT/driver.log"
fi

oracle_gate=0
port_title=0
port_hangar=0
retained=0
deadline=$((SECONDS + 205))
while (( SECONDS < deadline )); do
    if (( oracle_gate == 0 )) &&
       grep -a -q 'positive-control threshold reached: watch index 0 callbacks=10000' "$OUT/oracle.log" &&
       grep -a -q 'origin=0x00790400 width=1024' "$OUT/oracle.log" &&
       grep -a -qi 'origin=0x006ab400 width=512' "$OUT/oracle.log"; then
        oracle_gate=1
        print "oracle_controls=passed whole_rdram=10000 title=1 hangar=1" | tee -a "$OUT/driver.log"
    fi
    if (( port_title == 0 )) &&
       grep -a -q '^\[phase\] vi_width=1024 .*origin=0x00790400' "$OUT/port.log"; then
        port_title=1
        print "port_title=observed" | tee -a "$OUT/driver.log"
    fi
    if (( port_hangar == 0 )) &&
       grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/port.log"; then
        port_hangar=1
        print "port_hangar=observed; retaining_45s" | tee -a "$OUT/driver.log"
        sleep 45
        kill_tree "$PORT_PID"
        retained=1
    fi
    kill -0 "$PORT_PID" 2>/dev/null || (( port_hangar == 1 )) || break
    sleep 1
done
kill_tree "$KEY_PID"
kill_tree "$PORT_PID"
wait "$KEY_PID" 2>/dev/null || true
wait "$PORT_PID" 2>/dev/null
port_rc=$?
if kill -0 "$ORACLE_PID" 2>/dev/null; then
    deadline=$((SECONDS + 25))
    while kill -0 "$ORACLE_PID" 2>/dev/null && (( SECONDS < deadline )); do sleep 1; done
fi
kill_tree "$ORACLE_PID"
wait "$ORACLE_PID" 2>/dev/null
oracle_rc=$?

retail_writer=0
grep -a -q 'writer-pc-phase origin=0x006ab400 width=512 watch=1 range=\[0x00166450,0x00169450)' "$OUT/oracle.log" &&
grep -a -Eq 'writer-pc pc=0x[0-9a-f]+ n=[1-9]' "$OUT/oracle.log" && retail_writer=1
ring_watch=0
grep -a -q 'watch write \[0x00166450,0x00169450):' "$OUT/oracle.log" && ring_watch=1
ring_snapshot=0
grep -a -Eq 'post-value snapshot watch=1 bytes=12288 nonzero=[1-9]' "$OUT/oracle.log" && ring_snapshot=1
print "oracle_rc=$oracle_rc port_rc=$port_rc oracle_controls=$oracle_gate retail_writer=$retail_writer ring_watch=$ring_watch ring_snapshot=$ring_snapshot port_title=$port_title port_hangar=$port_hangar retained=$retained" | tee -a "$OUT/driver.log"

awk -v table="$OUT/provenance-table.tsv" '
function val(name, i) { for (i=1;i<=NF;i++) if (index($i,name"=")==1) return substr($i,length(name)+2); return "" }
function norm(v) { sub(/^0[xX]/,"",v); return tolower(v) }
function hex(v, s,i,c,d,n) { s=norm(v); n=0; for(i=1;i<=length(s);i++){c=substr(s,i,1);d=index("0123456789abcdef",c)-1;if(d<0)return -1;n=n*16+d} return n }
function phys(v, s) { s=norm(v); if(length(s)==8&&substr(s,1,2)=="80")s=substr(s,3); return s }
function wk(v) { return (v+0)==1 ? "guest-store" : ((v+0)==2 ? "image-dma" : "none") }
BEGIN { print "phase\twidth\torigin\tstage_event\tpcm_event\tkind\tdest\tlen\tstage_fnv\tstage_nz\tpcm_fnv\tpcm_nz\tcallsite\twriter_kind\twriter_pc\twriter_phys\twriter_writes\twriter_sequence\twriter_value\tstage_before_pcm" > table }
$1=="[audtask-image-stage-row]" {
    if((val("nz")+0)==0||(val("width")+0)!=512||norm(val("origin"))!="6ab400")next
    d=phys(val("dest")); if(hex(d)<1467472||hex(d)>=1479760)next
    stage_dest[d]=1
    ++sn; se[sn]=val("event")+0; sd[sn]=d; sf[sn]=norm(val("fnv")); sz[sn]=val("nz")+0; sl[sn]=norm(val("len")); next
}
$1=="[audio-join-pcm]" {
    if((val("width")+0)!=512||norm(val("origin"))!="6ab400")next
    d=phys(val("guest")); if(hex(d)<1467472||hex(d)>=1479760||(hex(d)-1467472)%768!=0)next
    if(!(d in stage_dest))next
    ++pn; pp[pn]=val("phase"); pe[pn]=val("event")+0; pk[pn]=val("kind"); pd[pn]=d; pl[pn]=norm(val("bytes")); pf[pn]=norm(val("fnv")); pz[pn]=val("nz")+0; pc[pn]=norm(val("callsite")); pkw[pn]=val("writer_kind")+0; pwp[pn]=norm(val("writer_pc")); pwr[pn]=norm(val("writer_phys")); pww[pn]=val("writer_writes")+0; pws[pn]=val("writer_sequence")+0; pwv[pn]=norm(val("writer_value")); next
}
END {
    for(i=1;i<=pn;i++) {
        best=-1; for(j=1;j<=sn;j++) if(sd[j]==pd[i]&&se[j]<=pe[i]&&(best<0||se[j]>se[best]))best=j
        if(best>=0){be=se[best];bf=sf[best];bz=sz[best];bl=sl[best];before="yes"}else{be="NA";bf="NA";bz="NA";bl="NA";before="NA"}
        print pp[i]"\t512\t0x6ab400\t"be"\t"pe[i]"\t"pk[i]"\t0x"pd[i]"\t0x"pl[i]"\t"bf"\t"bz"\t"pf[i]"\t"pz[i]"\t0x"pc[i]"\t"wk(pkw[i])"\t0x"pwp[i]"\t0x"pwr[i]"\t"pww[i]"\t"pws[i]"\t0x"pwv[i]"\t"before >> table
    }
    print "stage_rows="sn" pcm_rows="pn
}' "$OUT/port.log" > "$OUT/provenance-counts.txt"

awk -F '\t' '
NR==1 { next }
{ d=$7; if($10+0>0) { stage[d]=1; sf[d]=$9; sn[d]=$10 }
 if(!(d in stage)) next
 if($6=="source" && $12+0>0 && !(d in src)) { src[d]=$5; src_fnv[d]=$11; src_nz[d]=$12 }
 if($6=="consumer" && $12+0>0 && !(d in consumer)) { consumer[d]=$5; consumer_fnv[d]=$11; consumer_nz[d]=$12 }
 if($12+0==0 && (d in src) && (d in consumer) && !(d in zero) && $5+0>consumer[d]+0) { zero[d]=$5; zero_kind[d]=$14; zero_pc[d]=$15; zero_writes[d]=$17; zero_seq[d]=$18; zero_value[d]=$19 }
}
END {
 print "dest\tstage_fnv\tstage_nz\tfirst_source_nonzero\tfirst_consumer_nonzero\tfirst_later_zero\tzero_writer_kind\tzero_writer_pc\tzero_writer_writes\tzero_writer_sequence\tzero_writer_value"
 for(d in stage) print d"\t"sf[d]"\t"sn[d]"\t"(src[d]+0)"\t"(consumer[d]+0)"\t"(zero[d]+0)"\t"zero_kind[d]"\t"zero_pc[d]"\t"(zero_writes[d]+0)"\t"(zero_seq[d]+0)"\t"zero_value[d]
}' "$OUT/provenance-table.tsv" | sort -k1,1 > "$OUT/dynamic-slot-summary.tsv"
sed -n '1,10000p' "$OUT/provenance-counts.txt" >> "$OUT/driver.log"
sed -n '1,10000p' "$OUT/dynamic-slot-summary.tsv" >> "$OUT/driver.log"

stage_rows=$(sed -n 's/.*stage_rows=\([0-9]*\).*/\1/p' "$OUT/provenance-counts.txt")
pcm_rows=$(sed -n 's/.*pcm_rows=\([0-9]*\).*/\1/p' "$OUT/provenance-counts.txt")
writer_rows=$(grep -a -c '^\[pcm-writer\]' "$OUT/port.log" || true)
ring_bytes=12288
ring_nonzero=$(sed -n 's/.*post-value snapshot watch=1 bytes=12288 nonzero=\([0-9]*\).*/\1/p' "$OUT/oracle.log" | tail -1)
target_slot=$(awk -F '\t' 'NR>1 && $4+0>0 && $5+0>0 && $6+0>0 && $8=="image-dma" {print $1; exit}' "$OUT/dynamic-slot-summary.tsv")
target_nonzero_lower_bound=0
if [[ -n "$ring_nonzero" && -n "$target_slot" ]]; then
    target_nonzero_lower_bound=$((ring_nonzero - (ring_bytes - 768)))
    (( target_nonzero_lower_bound < 0 )) && target_nonzero_lower_bound=0
fi
print "retail_ring_bytes=$ring_bytes retail_ring_nonzero=${ring_nonzero:-0} exact_zero_slot=$target_slot exact_slot_nonzero_lower_bound=$target_nonzero_lower_bound" | tee -a "$OUT/driver.log"
if (( oracle_gate == 0 || retail_writer == 0 || ring_watch == 0 || ring_snapshot == 0 || port_title == 0 || port_hangar == 0 || retained == 0 || stage_rows == 0 || pcm_rows == 0 || writer_rows == 0 || ${#target_slot} == 0 )); then
    print "verdict=H-CoverageInvalid" | tee -a "$OUT/driver.log"
elif (( target_nonzero_lower_bound > 0 )); then
    print "verdict=H-PortOnlyZeroFill" | tee -a "$OUT/driver.log"
else
    print "verdict=H-SlotRotation" | tee -a "$OUT/driver.log"
fi
exit 0
