#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2327_m5_task_ordinal_prepost_join}
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
    ROGUESQ_LOG_VI_CALLERS=1 ROGUESQ_LOG_FILTER_VOICE_AUDIT=1
    ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1
)

print "oracle_start" > "$OUT/driver.log"
env "$ORACLE" \
    --core "$ORACLE_CORE" --rom "$ORACLE_ROM" --video "$ORACLE_VIDEO" \
    --secs 75 \
    --watch-write 0x0:0x800000 \
    --watch-write 0x166000:0x16A000 \
    --watch-write 0x141AD0:0x141AF0 \
    --watch-write 0xA0F50:0xA0F54 \
    --watch-write 0x1498A:0x1498C \
    --watch-write 0x154620:0x154624 \
    --hit-cap 40 \
    --watch-pc 0x8008EB8C,0x8008EBBC,0x80094648 \
    --pc-phase-log-width 0x006AB400:512 \
    --pc-hist-phase 0x006AB400:512 --pc-hist-watch 2 \
    --post-value-watch 2 \
    --post-value-pc 0x8008EB8C,0x8008EBBC,0x80094648 \
    --vi-trace --press "$PRESS" > "$OUT/oracle.log" 2>&1
oracle_rc=$?

oracle_gate=1
(( oracle_rc == 0 )) || oracle_gate=0
for marker in \
    '[oracle] watch write [0x00000000,0x00800000):' \
    '[oracle] watch write [0x00166000,0x0016a000):' \
    '[oracle] watch write [0x00141ad0,0x00141af0):' \
    '[oracle] watch write [0x000a0f50,0x000a0f54):' \
    '[oracle] watch write [0x00154620,0x00154624):'; do
    grep -a -F "$marker" "$OUT/oracle.log" | grep -Eq '[1-9][0-9]* hit' || oracle_gate=0
done
grep -a -F '[oracle] watch write [0x0001498a,0x0001498c): 0 hit' "$OUT/oracle.log" >/dev/null || oracle_gate=0
grep -a -F 'origin=0x00790400' "$OUT/oracle.log" >/dev/null || oracle_gate=0
grep -a -F 'origin=0x006ab400' "$OUT/oracle.log" >/dev/null || oracle_gate=0
grep -a -F '[oracle] writer-pc-phase origin=0x006ab400 width=512 watch=2 range=' "$OUT/oracle.log" >/dev/null || oracle_gate=0
grep -a -F '[oracle] writer-pc pc=0x8008eb8c n=' "$OUT/oracle.log" >/dev/null || oracle_gate=0
grep -a -F '[oracle] writer-pc pc=0x8008ebbc n=' "$OUT/oracle.log" >/dev/null || oracle_gate=0
grep -a -F '[oracle] writer-pc pc=0x80094648 n=' "$OUT/oracle.log" >/dev/null || oracle_gate=0
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
    ( cd "$BUILD" && exec env ${=COMMON} ROGUESQ_AUDIO_UCODE="$audio" ./RogueSquadron64Recomp ) > "$log" 2>&1 &
    GAME_PID=$!
    print "${name}_pid=$GAME_PID" | tee -a "$OUT/driver.log"
    local window_ok=0
    wait_for_window "$GAME_PID" && window_ok=1
    if (( window_ok )); then
        send_keys "$name" "$GAME_PID" &
        KEY_PID=$!
    else
        print "${name}_window=missing" | tee -a "$OUT/driver.log"
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
    (( hangar )) || print "${name}_hangar=missing" | tee -a "$OUT/driver.log"
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

for name in stub image; do
    print -- "--- $name controls ---" >> "$OUT/driver.log"
    for marker in '[vi-callers-control]' '[filter-voice-audit-control]' '[audtask-abi]' '[audtask-image-stage-row]' '[audtask-image-join]' '[audtask-join]' '[audtask-join-range]' '[audio-return]' '[m5-audio-join-control]' '[m5-audio-event]' '[pcm-boundary-source]' '[pcm-boundary-consumer]' '[CRASH]' '[ABORT]'; do
        print "$marker=$(grep -a -F -c "$marker" "$OUT/$name.log" 2>/dev/null || true)" >> "$OUT/driver.log"
    done
    print "title=$(grep -a -c '^\[phase\] vi_width=1024 .*origin=0x00790400' "$OUT/$name.log" 2>/dev/null || true)" >> "$OUT/driver.log"
    print "hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/$name.log" 2>/dev/null || true)" >> "$OUT/driver.log"
done

python3 - "$OUT/image.log" "$OUT/task-ordinal-table.tsv" "$OUT/task-ordinal-events.tsv" "$OUT/task-ordinal-summary.tsv" <<'PY'
import re
import sys
from collections import Counter, defaultdict

log_path, table_path, events_path, summary_path = sys.argv[1:]
kv = re.compile(r'([^=\s]+)=([^\s]+)')
def integer(v, default=0):
    try: return int(v, 0)
    except (TypeError, ValueError): return default
def parse(line):
    p = line.split()
    return (p[0] if p else "", dict(kv.findall(line)))
def scope(row):
    return (integer(row.get("phase")), integer(row.get("width")), integer(row.get("origin")))
def same_scope(a, b):
    return scope(a) == scope(b)

stages, joins, tasks, dmaranges, pcms, lifecycle = [], [], [], [], [], []
phase = {"phase":"", "width":"", "origin":""}
with open(log_path, errors="replace") as stream:
    for seq, line in enumerate(stream, 1):
        tag, f = parse(line)
        for key in ("phase", "width", "origin"):
            if key in f: phase[key] = f[key]
        if tag in ("[audtask-image-stage-row]", "[audtask-image-join]", "[audtask-join]", "[audtask-dma-range]", "[audio-join-pcm]", "[m5-audio-event]"):
            f = {**phase, **f}
        if tag == "[audtask-image-stage-row]": stages.append({"seq":seq, **f})
        elif tag == "[audtask-image-join]": joins.append({"seq":seq, **f})
        elif tag == "[audtask-join]": tasks.append({"seq":seq, **f})
        elif tag == "[audtask-dma-range]": dmaranges.append({"seq":seq, **f})
        elif tag == "[audio-join-pcm]": pcms.append({"seq":seq, **f})
        elif tag == "[m5-audio-event]": lifecycle.append({"seq":seq, **f})

stages = [s for s in stages if integer(s.get("width")) == 512 and integer(s.get("origin")) == 0x6AB400 and integer(s.get("stage")) in (2, 3) and integer(s.get("nz")) > 0]
stages.sort(key=lambda x:x["seq"])
def match_join(stage):
    rows = [j for j in joins if j.get("arm") == stage.get("arm") and j.get("ordinal") == stage.get("ordinal") and j.get("row") == stage.get("row") and j.get("stage_event") == stage.get("event")]
    return rows[-1] if rows else {}
def match_task(stage, join):
    candidates = [t for t in tasks if same_scope(t, stage)]
    candidates = candidates or tasks
    event = integer(stage.get("event"))
    containing = [t for t in candidates if integer(t.get("begin")) <= event <= integer(t.get("end"))]
    if containing: return min(containing, key=lambda t: abs(integer(t.get("end")) - event))
    return min(candidates, key=lambda t: abs(integer(t.get("begin")) - event)) if candidates else {}
def signed(a, b):
    return "NA" if not a or not b or integer(a) == 0 or integer(b) == 0 else str(integer(a) - integer(b))
def m5_detail(stage, join, task):
    event = integer(stage.get("event"))
    return [e for e in lifecycle if e.get("arm") == stage.get("arm") and same_scope(e, stage) and abs(integer(e.get("event")) - event) <= 512]
def m5_wrong_ordinal(stage, task):
    lo = integer(task.get("begin")) - 256
    hi = integer(task.get("end")) + 256
    return [e for e in lifecycle if e.get("arm") == stage.get("arm") and lo <= integer(e.get("event")) <= hi and not (e.get("ordinal") == stage.get("ordinal") and e.get("row") == stage.get("row") and same_scope(e, stage))]

header = ["arm","phase","width","origin","ordinal","row","stage","dest","len","stage_event","complete_event","source_event","consumer_event","task_n","task_begin","task_end","m5_pre_n","m5_post_n","m5_wrong_ordinal_n","m5_details","containing_task_n","previous_task_n","next_task_n","task_complete","task_dma_count","stage_dma_match","task_dma_ranges","task_source_matches","task_consumer_matches","task_pcm_source_n","task_pcm_consumer_n","task_pcm_nz_source_n","task_pcm_nz_consumer_n","task_order"]
rows, raw = [], []
for stage in stages:
    join = match_join(stage)
    task = match_task(stage, join)
    scoped_tasks = [t for t in tasks if same_scope(t, stage)] or tasks
    stage_event = integer(stage.get("event"))
    containing = [t for t in scoped_tasks if integer(t.get("begin")) <= stage_event <= integer(t.get("end"))]
    previous = [t for t in scoped_tasks if integer(t.get("end")) < stage_event]
    following = [t for t in scoped_tasks if integer(t.get("begin")) > stage_event]
    containing = min(containing, key=lambda t: abs(integer(t.get("begin")) - stage_event)) if containing else {}
    previous = max(previous, key=lambda t: integer(t.get("end"))) if previous else {}
    following = min(following, key=lambda t: integer(t.get("begin"))) if following else {}
    if containing:
        task = containing
    task_join = task
    events = m5_detail(stage, join, task)
    wrong = m5_wrong_ordinal(stage, task)
    task_n = task.get("n", "")
    task_dma = [d for d in dmaranges if d.get("n") == task_n and (same_scope(d, stage) or not d.get("origin"))]
    stage_dma = [d for d in task_dma if integer(d.get("dram", "").split("..", 1)[0]) == integer(stage.get("dest")) and integer(d.get("len")) == integer(stage.get("len")) and integer(d.get("payload_fnv"), 16) == integer(stage.get("fnv"), 16) and integer(d.get("payload_nz")) == integer(stage.get("nz"))]
    task_begin, task_end = integer(task.get("begin")), integer(task.get("end"))
    task_pcm = [p for p in pcms if same_scope(p, stage) and task_begin <= integer(p.get("event")) <= task_end + 512]
    pcm_source = [p for p in task_pcm if p.get("kind") == "source"]
    pcm_consumer = [p for p in task_pcm if p.get("kind") == "consumer"]
    source_nz = [p for p in pcm_source if integer(p.get("nz")) > 0]
    consumer_nz = [p for p in pcm_consumer if integer(p.get("nz")) > 0]
    order = "complete+pcm" if task_join and task_join.get("complete") == "1" and task_join.get("source_matches", "0") != "0" and task_join.get("consumer_matches", "0") != "0" else ("complete-only" if task_join and task_join.get("complete") == "1" else "internal")
    pre = [e for e in events if integer(e.get("event")) < integer(stage.get("event"))]
    post = [e for e in events if integer(e.get("event")) > integer(stage.get("event"))]
    detail = []
    for e in events + wrong:
        is_wrong = e in wrong
        detail.append("%s%s@%s:dstage=%s:dstart=%s:dend=%s:dcomplete=%s:dsource=%s:dconsumer=%s:active=%s:idx=%s:dest=%s" % ("wrong-" if is_wrong else "", e.get("kind",""), e.get("event",""), signed(e.get("event"), stage.get("event")), signed(e.get("event"), task.get("begin")), signed(e.get("event"), task.get("end")), signed(e.get("event"), join.get("complete_event")), signed(e.get("event"), join.get("source_event")), signed(e.get("event"), join.get("consumer_event")), e.get("active",""), e.get("idx",""), e.get("dest","")))
        raw.append([stage.get("arm",""), stage.get("ordinal",""), stage.get("row",""), stage.get("dest",""), stage.get("event",""), e.get("event",""), signed(e.get("event"), stage.get("event")), signed(e.get("event"), task.get("begin")), signed(e.get("event"), task.get("end")), e.get("kind",""), e.get("active",""), e.get("idx",""), e.get("dest","")])
    dma_desc = ";".join("%s:%s:%s:%s:%s" % (d.get("event",""), d.get("dram",""), d.get("len",""), d.get("payload_fnv",""), d.get("payload_nz","")) for d in task_dma)
    rows.append([stage.get("arm",""),stage.get("phase",""),stage.get("width",""),stage.get("origin",""),stage.get("ordinal",""),stage.get("row",""),stage.get("stage",""),stage.get("dest",""),stage.get("len",""),stage.get("event",""),join.get("complete_event",""),join.get("source_event",""),join.get("consumer_event",""),task.get("n",""),task.get("begin",""),task.get("end",""),len(pre),len(post),len(wrong),";".join(detail),containing.get("n",""),previous.get("n",""),following.get("n",""),task_join.get("complete",""),len(task_dma),len(stage_dma),dma_desc,task_join.get("source_matches",""),task_join.get("consumer_matches",""),len(pcm_source),len(pcm_consumer),len(source_nz),len(consumer_nz),order])

with open(table_path,"w") as out:
    out.write("\t".join(header)+"\n")
    for row in rows: out.write("\t".join(map(str,row))+"\n")
with open(events_path,"w") as out:
    out.write("arm\tordinal\trow\tdest\tstage_event\tm5_event\tdelta_stage\tdelta_task_begin\tdelta_task_end\tkind\tactive\tidx\tevent_dest\n")
    for row in raw: out.write("\t".join(map(str,row))+"\n")
counts = Counter()
for stage in stages:
    for e in m5_detail(stage, match_join(stage), match_task(stage, match_join(stage))): counts[e.get("kind","")] += 1
with open(summary_path,"w") as out:
    out.write("metric\tvalue\n")
    out.write(f"target_stage_rows\t{len(stages)}\n")
    out.write(f"lifecycle_rows\t{len(raw)}\n")
    for key in sorted(counts): out.write(f"m5_{key}\t{counts[key]}\n")
print(f"target_stage_rows={len(stages)} lifecycle_rows={len(raw)}")
PY

sed -n '1,140p' "$OUT/task-ordinal-table.tsv" >> "$OUT/driver.log"
sed -n '1,80p' "$OUT/task-ordinal-summary.tsv" >> "$OUT/driver.log"

stub_hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/stub.log" 2>/dev/null || true)
image_hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/image.log" 2>/dev/null || true)
stub_controls=$(grep -a -c '^\[audtask-abi\]' "$OUT/stub.log" 2>/dev/null || true)
image_controls=$(grep -a -c '^\[audtask-abi\]' "$OUT/image.log" 2>/dev/null || true)
stub_vi=$(grep -a -c '^\[vi-callers-control\]' "$OUT/stub.log" 2>/dev/null || true)
image_vi=$(grep -a -c '^\[vi-callers-control\]' "$OUT/image.log" 2>/dev/null || true)
stub_filter=$(grep -a -c '^\[filter-voice-audit-control\]' "$OUT/stub.log" 2>/dev/null || true)
image_filter=$(grep -a -c '^\[filter-voice-audit-control\]' "$OUT/image.log" 2>/dev/null || true)
image_join_control=$(grep -a -c '^\[m5-audio-join-control\]' "$OUT/image.log" 2>/dev/null || true)
target_stage_rows=$(awk -F '\t' 'NR>1 {n++} END {print n+0}' "$OUT/task-ordinal-table.tsv")
same_task_pre=$(awk -F '\t' 'NR>1 && $21!="" {n++} END {print n+0}' "$OUT/task-ordinal-table.tsv")
same_task_post=$(awk -F '\t' 'NR>1 && $22!="" {n++} END {print n+0}' "$OUT/task-ordinal-table.tsv")
next_task_rows=$(awk -F '\t' 'NR>1 && $23!="" {n++} END {print n+0}' "$OUT/task-ordinal-table.tsv")
stage_dma_matches=$(awk -F '\t' 'NR>1 && $26>0 {n++} END {print n+0}' "$OUT/task-ordinal-table.tsv")
task_pcm_rows=$(awk -F '\t' 'NR>1 && $30>0 && $31>0 {n++} END {print n+0}' "$OUT/task-ordinal-table.tsv")
task_complete_rows=$(awk -F '\t' 'NR>1 && $24==1 {n++} END {print n+0}' "$OUT/task-ordinal-table.tsv")
task_output_pcm_rows=$(awk -F '\t' 'NR>1 && $24==1 && $26>0 && $30>0 && $31>0 {n++} END {print n+0}' "$OUT/task-ordinal-table.tsv")
print "controls oracle=$oracle_gate stub_abi=$stub_controls image_abi=$image_controls stub_vi=$stub_vi image_vi=$image_vi stub_filter=$stub_filter image_filter=$image_filter image_join=$image_join_control" | tee -a "$OUT/driver.log"
print "table target_stage_rows=$target_stage_rows containing_task_rows=$same_task_pre previous_task_rows=$same_task_post next_task_rows=$next_task_rows stage_dma_matches=$stage_dma_matches task_pcm_rows=$task_pcm_rows task_complete_rows=$task_complete_rows task_output_pcm_rows=$task_output_pcm_rows" | tee -a "$OUT/driver.log"

if (( oracle_gate == 0 || stub_hangar == 0 || image_hangar == 0 || stub_controls == 0 || image_controls == 0 || stub_vi == 0 || image_vi == 0 || image_join_control == 0 || target_stage_rows == 0 )); then
    verdict=H-CoverageInvalid
elif (( target_stage_rows > 0 && stage_dma_matches == target_stage_rows && task_output_pcm_rows == target_stage_rows )); then
    verdict=H-ContainingTaskOutputClosed
elif (( same_task_pre > 0 )); then
    verdict=H-ContainingTaskInternalOnly
elif (( next_task_rows > 0 )); then
    verdict=H-StageBeforeLaterTask
elif (( same_task_post > 0 )); then
    verdict=H-StageAfterEarlierTask
else
    verdict=H-StageNoTaskBoundary
fi
print "verdict=$verdict oracle_controls=$oracle_gate target_stage_rows=$target_stage_rows containing_task_rows=$same_task_pre previous_task_rows=$same_task_post next_task_rows=$next_task_rows stage_dma_matches=$stage_dma_matches task_pcm_rows=$task_pcm_rows task_output_pcm_rows=$task_output_pcm_rows" | tee -a "$OUT/driver.log"
exit 0
