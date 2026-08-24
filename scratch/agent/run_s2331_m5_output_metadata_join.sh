#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2331_m5_output_metadata_join}
OUT="$ROOT/scratch/agent/$TAG"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
ORACLE_CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ORACLE_ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
ORACLE_VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
WINCTL="$BUILD/winctl"

[[ "$TAG" != .* ]] || exit 2
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
    --watch-write 0x165000:0x16B000 \
    --watch-write 0x141AD0:0x141AF0 \
    --watch-write 0xA0F50:0xA0F54 \
    --watch-write 0x1498A:0x1498C \
    --watch-write 0x154620:0x154624 \
    --hit-cap 40 \
    --watch-pc 0x8008EB8C,0x8008EBBC,0x80094648 \
    --pc-phase-log-width 0x006AB400:512 \
    --pc-hist-phase 0x006AB400:512 --pc-hist-watch 1 --pc-hist-watch 2 \
    --post-value-watch 1 \
    --post-value-pc 0x8008EB8C,0x8008EBBC,0x80094648 \
    --post-value-pc-detail --vi-trace --press "$PRESS" > "$OUT/oracle.log" 2>&1
oracle_rc=$?

oracle_gate=1
(( oracle_rc == 0 )) || oracle_gate=0
for marker in \
    '[oracle] watch write [0x00000000,0x00800000):' \
    '[oracle] watch write [0x00165000,0x0016b000):' \
    '[oracle] watch write [0x00141ad0,0x00141af0):' \
    '[oracle] watch write [0x000a0f50,0x000a0f54):' \
    '[oracle] watch write [0x00154620,0x00154624):'; do
    grep -a -F "$marker" "$OUT/oracle.log" | grep -Eq '[1-9][0-9]* hit' || oracle_gate=0
done
grep -a -F '[oracle] watch write [0x0001498a,0x0001498c): 0 hit' "$OUT/oracle.log" >/dev/null || oracle_gate=0
grep -a -F 'origin=0x00790400' "$OUT/oracle.log" >/dev/null || oracle_gate=0
grep -a -F 'origin=0x006ab400' "$OUT/oracle.log" >/dev/null || oracle_gate=0
grep -a -F '[oracle] writer-pc-phase origin=0x006ab400 width=512 watch=1 range=' "$OUT/oracle.log" >/dev/null || oracle_gate=0
for pc in 8008eb8c 8008ebbc 80094648; do
    grep -a -F "[oracle] writer-pc pc=0x$pc n=" "$OUT/oracle.log" >/dev/null || oracle_gate=0
done
print "oracle_rc=$oracle_rc oracle_controls=$oracle_gate" | tee -a "$OUT/driver.log"
grep -a -E '^\[oracle\] (done:|watch write \[0x00000000|watch write \[0x00165000|watch write \[0x00141ad0|watch write \[0x000a0f50|watch write \[0x0001498a|watch write \[0x00154620|writer-pc-phase|post-value watch=1|post-value snapshot watch=1|post-value-pc-row)' "$OUT/oracle.log" | tail -80 >> "$OUT/driver.log" || true
if (( oracle_gate == 0 )); then
    print "verdict=H-CoverageInvalid oracle_controls=0" | tee -a "$OUT/driver.log"
    exit 5
fi

STUB_PID=""
IMAGE_PID=""
STUB_KEY_PID=""
IMAGE_KEY_PID=""
cleanup_game() {
    local pid="$1"
    local keypid="$2"
    if [[ -n "$keypid" ]] && kill -0 "$keypid" 2>/dev/null; then kill -9 "$keypid" 2>/dev/null || true; fi
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        /usr/bin/pkill -KILL -P "$pid" 2>/dev/null || true
        kill -9 "$pid" 2>/dev/null || true
    fi
}
cleanup_all() {
    cleanup_game "$STUB_PID" "$STUB_KEY_PID"
    cleanup_game "$IMAGE_PID" "$IMAGE_KEY_PID"
}
trap cleanup_all EXIT INT TERM

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

start_arm() {
    local name="$1"
    local audio="$2"
    local log="$OUT/$name.log"
    ( cd "$BUILD" && exec env ${=COMMON} ROGUESQ_AUDIO_UCODE="$audio" ROGUESQ_DRAIN_INLOOP_TICK=1 ./RogueSquadron64Recomp ) > "$log" 2>&1 &
    print $!
}

run_arm() {
    local name="$1"
    local audio="$2"
    local pid=""
    local keypid=""
    pid=$(start_arm "$name" "$audio")
    print "${name}_pid=$pid audio=$audio drain_tick=1" | tee -a "$OUT/driver.log"
    if wait_for_window "$pid"; then
        send_keys "$name" "$pid" & keypid=$!
    else
        print "${name}_window=missing" | tee -a "$OUT/driver.log"
    fi
    local hangar=0
    local deadline=$((SECONDS + 240))
    while (( SECONDS < deadline )); do
        if grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/$name.log"; then
            hangar=1
            print "${name}_hangar=observed; retaining_15s" | tee -a "$OUT/driver.log"
            sleep 15
            break
        fi
        if ! kill -0 "$pid" 2>/dev/null; then break; fi
        sleep 1
    done
    (( hangar )) || print "${name}_hangar=missing" | tee -a "$OUT/driver.log"
    cleanup_game "$pid" "$keypid"
    wait "$keypid" 2>/dev/null || true
    wait "$pid" 2>/dev/null
    local rc=$?
    print "${name}_rc=$rc ${name}_hangar=$hangar" | tee -a "$OUT/driver.log"
}

print "arms=stub,image; sequential validated input schedule; drain_tick=1" | tee -a "$OUT/driver.log"
run_arm stub 0
run_arm image 1

for name in stub image; do
    log="$OUT/$name.log"
    print -- "--- $name controls ---" >> "$OUT/driver.log"
    for marker in \
        '[vi-callers-control]' '[filter-voice-audit-control]' '[audtask-abi]' \
        '[audtask-dma-row]' '[audtask-dma-range]' '[audtask-image-stage-row]' \
        '[audtask-image-join]' '[audtask-join]' '[audtask-join-range]' \
        '[audio-return]' '[audio-sp-route] edge=guest-receive' \
        '[m5-audio-join-control]' '[pcm-boundary-source]' \
        '[pcm-boundary-consumer]' '[m5-audio-event]' '[CRASH]' '[ABORT]'; do
        print "$marker=$(grep -a -F -c "$marker" "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    done
    print "title=$(grep -a -c '^\[phase\] vi_width=1024 .*origin=0x00790400' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    print "hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
done

python3 - "$OUT/image.log" "$OUT/oracle.log" "$OUT/metadata-join.tsv" "$OUT/metadata-events.tsv" "$OUT/metadata-summary.tsv" <<'PY' | tee -a "$OUT/driver.log"
import re
import sys
from collections import Counter

image_log, oracle_log, table_path, events_path, summary_path = sys.argv[1:]
TOKEN = re.compile(r"([^=\s]+)=([^\s]+)")

def integer(value, default=0):
    if isinstance(value, int):
        return value
    try:
        return int(value, 0)
    except (TypeError, ValueError):
        try:
            if isinstance(value, str) and re.fullmatch(r"[0-9A-Fa-f]+", value):
                return int(value, 16)
        except (TypeError, ValueError):
            pass
        return default

def parse(line):
    fields = dict(TOKEN.findall(line))
    words = line.split()
    return (words[0] if words else "", fields)

def scope(row):
    return (integer(row.get("phase")), integer(row.get("width")), integer(row.get("origin")))

def same_scope(a, b):
    return scope(a) == scope(b)

stages = []
joins = []
tasks = []
abis = []
dmas = []
ranges = []
join_ranges = []
pcms = []
lifecycle = []
with open(image_log, errors="replace") as stream:
    for seq, line in enumerate(stream, 1):
        tag, fields = parse(line)
        row = {"seq": seq, **fields}
        if tag == "[audtask-image-stage-row]":
            stages.append(row)
        elif tag == "[audtask-image-join]":
            joins.append(row)
        elif tag == "[audtask-join]":
            tasks.append(row)
        elif tag == "[audtask-abi]":
            abis.append(row)
        elif tag == "[audtask-dma-row]":
            dmas.append(row)
        elif tag == "[audtask-dma-range]":
            ranges.append(row)
        elif tag == "[audtask-join-range]":
            join_ranges.append(row)
        elif tag in ("[pcm-boundary-source]", "[pcm-boundary-consumer]"):
            pcms.append({"seq": seq, "source": tag.endswith("source]"), **fields})
        elif tag == "[m5-audio-event]":
            lifecycle.append(row)

target = [row for row in stages
          if integer(row.get("width")) == 512 and integer(row.get("origin")) == 0x6AB400
          and integer(row.get("stage")) in (2, 3)]
all_target_rows = len(target)
target = [row for row in target if integer(row.get("nz")) > 0]
target.sort(key=lambda row: row["seq"])

def nearest(rows, event):
    return min(rows, key=lambda row: abs(integer(row.get("event")) - event), default={})

def stage_join(stage):
    rows = [row for row in joins if row.get("arm") == stage.get("arm")
            and row.get("ordinal") == stage.get("ordinal")
            and row.get("row") == stage.get("row")
            and integer(row.get("stage_event")) == integer(stage.get("event"))]
    return rows[-1] if rows else {}

def task_for(stage):
    event = integer(stage.get("event"))
    candidates = [row for row in tasks if same_scope(row, stage)]
    containing = [row for row in candidates
                  if integer(row.get("begin")) <= event <= integer(row.get("end"))]
    if containing:
        row = min(containing, key=lambda item: integer(item.get("end")) - event)
        return row, "containing"
    return nearest(candidates, event), "nearest"

def metadata_for(task, stage):
    task_n = task.get("n", "")
    candidates = [row for row in abis if row.get("n") == task_n]
    abi = min(candidates, key=lambda row: abs(row["seq"] - stage["seq"]), default={})
    dma_rows = [row for row in dmas if row.get("n") == task_n and same_scope(row, stage)]
    dma = min(dma_rows, key=lambda row: abs(row["seq"] - stage["seq"]), default={})
    begin = integer(task.get("begin"))
    end = integer(task.get("end"))
    rr = [row for row in ranges if row.get("n") == task_n
          and begin <= integer(row.get("event")) <= end]
    jr = [row for row in join_ranges if row.get("task") == task_n
          and begin <= integer(row.get("dma_event")) <= end]
    return abi, dma, rr, jr

def image_pcms(stage):
    dest = integer(stage.get("dest"))
    length = integer(stage.get("len"))
    fnv = integer(stage.get("fnv"))
    nz = integer(stage.get("nz"))
    return [row for row in pcms if same_scope(row, stage)
            and (integer(row.get("rdram")) & 0x7FFFFF) == dest
            and integer(row.get("bytes")) == length
            and integer(row.get("fnv")) == fnv
            and integer(row.get("nz")) == nz]

def lifecycle_for(stage, task, join):
    same = [row for row in lifecycle if same_scope(row, stage)
            and row.get("ordinal") == stage.get("ordinal")
            and row.get("row") == stage.get("row")]
    complete = integer(join.get("complete_event"))
    post = [row for row in same if complete and integer(row.get("event")) > complete]
    lo = integer(task.get("begin")) - 256
    hi = complete + 256 if complete else integer(stage.get("event")) + 256
    prior = [row for row in lifecycle if lo <= integer(row.get("event")) <= hi
             and not (row.get("ordinal") == stage.get("ordinal")
                      and row.get("row") == stage.get("row")
                      and same_scope(row, stage))]
    return same, post, prior

def signed(event, base):
    if not event or not base:
        return "NA"
    return str(integer(event) - integer(base))

def lifecycle_sig(rows, base):
    return ";".join(
        f"{row.get('kind','')}@{signed(row.get('event'), base)}"
        f":active={row.get('active','')}:idx={row.get('idx','')}"
        f":dest={row.get('dest','')}:v0={row.get('value0','')}"
        for row in rows)

def range_sig(rows):
    return ";".join(
        f"i={row.get('i','')},dmem={row.get('dmem','')},len={row.get('len','')}"
        f",event={row.get('event','')},dram={row.get('dram','')}"
        f",out={row.get('output_overlap','')},yield={row.get('yield_overlap','')}"
        f",data={row.get('data_overlap','')},fnv={row.get('payload_fnv','')}"
        f",nz={row.get('payload_nz','')}"
        for row in rows)

def join_range_sig(rows):
    return ";".join(
        f"i={row.get('i','')},dma={row.get('dma_event','')},guest={row.get('guest','')}"
        f",len={row.get('len','')},src={row.get('source_event','')}"
        f",cons={row.get('consumer_event','')}"
        for row in rows)

retail_watch_hits = 0
retail_pcs = Counter()
with open(oracle_log, errors="replace") as stream:
    for line in stream:
        match = re.search(r"^\[oracle\] watch write \[0x00165000,0x0016b000\): (\d+) hit", line)
        if match:
            retail_watch_hits = int(match.group(1))
        match = re.search(r"^\[oracle\] writer-pc-phase origin=0x006ab400 width=512 watch=1 pc=(0x[0-9a-f]+) n=(\d+)", line)
        if match:
            retail_pcs[match.group(1)] += int(match.group(2))
retail_positive = retail_watch_hits > 0 and bool(retail_pcs)

header = [
    "arm", "phase", "width", "origin", "ordinal", "row", "stage", "stage_event",
    "dest", "len", "stage_fnv", "stage_nz", "complete_event", "classification",
    "task_relation", "task_n", "task_begin", "task_end", "type", "flags", "ucode",
    "data_ptr", "data_size", "output_buff", "output_buff_size", "yield_ptr", "yield_size",
    "dma_count", "dma_range_signature", "join_range_signature", "source_event",
    "consumer_event", "pcm_source_rows", "pcm_consumer_rows", "same_lifecycle",
    "post_stage_lifecycle", "prior_lifecycle", "retail_role", "retail_watch_hits",
    "retail_phase_pcs"
]
rows = []
events = []
for stage in target:
    join = stage_join(stage)
    task, relation = task_for(stage)
    abi, dma, rr, jr = metadata_for(task, stage)
    same, post, prior = lifecycle_for(stage, task, join)
    matches = image_pcms(stage)
    source_rows = [row for row in matches if row.get("source")]
    consumer_rows = [row for row in matches if not row.get("source")]
    base = stage.get("event", "")
    complete = join.get("complete_event", "")
    rows.append([
        stage.get("arm", ""), stage.get("phase", ""), stage.get("width", ""), stage.get("origin", ""),
        stage.get("ordinal", ""), stage.get("row", ""), stage.get("stage", ""), base,
        stage.get("dest", ""), stage.get("len", ""), stage.get("fnv", ""), stage.get("nz", ""),
        complete, join.get("classification", ""), relation, task.get("n", ""), task.get("begin", ""),
        task.get("end", ""), abi.get("type", dma.get("type", "")), abi.get("flags", dma.get("flags", "")),
        abi.get("ucode", dma.get("ucode", "")), abi.get("data_ptr", dma.get("data_ptr", "")),
        abi.get("data_size", dma.get("data_size", "")), abi.get("output_buff", dma.get("output_buff", "")),
        abi.get("output_buff_size", dma.get("output_buff_size", "")), abi.get("yield_ptr", dma.get("yield_ptr", "")),
        abi.get("yield_size", dma.get("yield_size", "")), dma.get("dma_count", ""), range_sig(rr),
        join_range_sig(jr), join.get("source_event", ""), join.get("consumer_event", ""),
        len(source_rows), len(consumer_rows), lifecycle_sig(same, base),
        lifecycle_sig(post, complete), lifecycle_sig(prior, task.get("begin", "")),
        "retail-target-window-written" if retail_positive else "retail-target-window-unqualified",
        retail_watch_hits, ",".join(f"{pc}:{n}" for pc, n in retail_pcs.items())
    ])
    for item in same + post + prior:
        events.append([stage.get("arm", ""), stage.get("ordinal", ""), stage.get("row", ""),
                       base, item.get("event", ""), signed(item.get("event"), base),
                       item.get("kind", ""), item.get("active", ""), item.get("idx", ""),
                       item.get("dest", ""), item.get("value0", "")])

with open(table_path, "w") as out:
    out.write("\t".join(header) + "\n")
    for row in rows:
        out.write("\t".join(str(value).replace("\t", " ") for value in row) + "\n")
with open(events_path, "w") as out:
    out.write("arm\tordinal\trow\tstage_event\tevent\tdelta\tkind\tactive\tidx\tdest\tvalue0\n")
    for row in events:
        out.write("\t".join(str(value) for value in row) + "\n")

classes = Counter(row[13] for row in rows)
post_rows = sum(bool(row[35]) for row in rows)
prior_rows = sum(bool(row[36]) for row in rows)
output_valid = sum(integer(row[23]) != 0 or integer(row[24]) != 0 or
                   "out=1" in row[28] for row in rows)
exact_pcm = sum(integer(row[32]) > 0 and integer(row[33]) > 0 for row in rows)
with open(summary_path, "w") as out:
    out.write("metric\tvalue\n")
    out.write(f"all_target_stage_rows\t{all_target_rows}\n")
    out.write(f"nonzero_target_stage_rows\t{len(rows)}\n")
    out.write(f"retail_target_watch_hits\t{retail_watch_hits}\n")
    out.write(f"retail_target_phase_pcs\t{len(retail_pcs)}\n")
    out.write(f"rows_with_output_metadata_or_overlap\t{output_valid}\n")
    out.write(f"rows_with_exact_pcm_source_consumer\t{exact_pcm}\n")
    out.write(f"rows_with_post_stage_lifecycle\t{post_rows}\n")
    out.write(f"rows_with_prior_lifecycle\t{prior_rows}\n")
    for key, value in sorted(classes.items()):
        out.write(f"classification_{key}\t{value}\n")

if not retail_positive or not rows:
    verdict = "H-CoverageInvalid"
elif output_valid == 0:
    verdict = "H-OutputBuffZero"
elif exact_pcm == len(rows) and post_rows == 0 and prior_rows:
    verdict = "H-PCMPathOnly"
elif output_valid > 0 and any("out=1" in row[28] or integer(row[23]) != 0 for row in rows):
    verdict = "H-DataPtrRole"
else:
    verdict = "H-RoleJoinUnresolved"
print(f"metadata all_target_stage_rows={all_target_rows} nonzero_target_stage_rows={len(rows)} classes={dict(classes)} retail_watch_hits={retail_watch_hits} retail_phase_pcs={len(retail_pcs)} output_valid={output_valid} exact_pcm={exact_pcm} post_stage_rows={post_rows} prior_rows={prior_rows} verdict={verdict}")
PY

sed -n '1,120p' "$OUT/metadata-summary.tsv" >> "$OUT/driver.log"
sed -n '1,40p' "$OUT/metadata-join.tsv" >> "$OUT/driver.log"

oracle_ok=$oracle_gate
stub_hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/stub.log" 2>/dev/null || true)
image_hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/image.log" 2>/dev/null || true)
stub_vi=$(grep -a -c '^\[vi-callers-control\]' "$OUT/stub.log" 2>/dev/null || true)
image_vi=$(grep -a -c '^\[vi-callers-control\]' "$OUT/image.log" 2>/dev/null || true)
stub_abi=$(grep -a -c '^\[audtask-abi\]' "$OUT/stub.log" 2>/dev/null || true)
image_abi=$(grep -a -c '^\[audtask-abi\]' "$OUT/image.log" 2>/dev/null || true)
stub_dma=$(grep -a -c '^\[audtask-dma-row\]' "$OUT/stub.log" 2>/dev/null || true)
image_dma=$(grep -a -c '^\[audtask-dma-row\]' "$OUT/image.log" 2>/dev/null || true)
stub_sp=$(grep -a -c '^\[audio-sp-route\] edge=guest-receive' "$OUT/stub.log" 2>/dev/null || true)
image_sp=$(grep -a -c '^\[audio-sp-route\] edge=guest-receive' "$OUT/image.log" 2>/dev/null || true)
stub_src=$(grep -a -c '^\[pcm-boundary-source\]' "$OUT/stub.log" 2>/dev/null || true)
stub_cons=$(grep -a -c '^\[pcm-boundary-consumer\]' "$OUT/stub.log" 2>/dev/null || true)
image_src=$(grep -a -c '^\[pcm-boundary-source\]' "$OUT/image.log" 2>/dev/null || true)
image_cons=$(grep -a -c '^\[pcm-boundary-consumer\]' "$OUT/image.log" 2>/dev/null || true)
image_stage=$(grep -a -c '^\[audtask-image-stage-row\]' "$OUT/image.log" 2>/dev/null || true)
image_join=$(grep -a -c '^\[audtask-image-join\]' "$OUT/image.log" 2>/dev/null || true)
image_join_control=$(grep -a -c '^\[m5-audio-join-control\]' "$OUT/image.log" 2>/dev/null || true)
stub_join_control=$(grep -a -c '^\[m5-audio-join-control\]' "$OUT/stub.log" 2>/dev/null || true)
filter_stub=$(grep -a -c '^\[filter-voice-audit-control\]' "$OUT/stub.log" 2>/dev/null || true)
filter_image=$(grep -a -c '^\[filter-voice-audit-control\]' "$OUT/image.log" 2>/dev/null || true)
table_rows=$(awk -F '\t' 'NR>1 {n++} END {print n+0}' "$OUT/metadata-join.tsv")
print "controls oracle=$oracle_ok stub_hangar=$stub_hangar image_hangar=$image_hangar stub_vi=$stub_vi image_vi=$image_vi stub_abi=$stub_abi image_abi=$image_abi stub_dma=$stub_dma image_dma=$image_dma stub_sp=$stub_sp image_sp=$image_sp stub_pcm=${stub_src}/${stub_cons} image_pcm=${image_src}/${image_cons} image_stage=$image_stage image_join=$image_join join_control=${stub_join_control}/${image_join_control} filter_control=${filter_stub}/${filter_image} table_rows=$table_rows" | tee -a "$OUT/driver.log"

if (( oracle_ok == 0 || stub_hangar == 0 || image_hangar == 0 || stub_vi == 0 || image_vi == 0 || stub_abi == 0 || image_abi == 0 || stub_dma == 0 || image_dma == 0 || stub_sp == 0 || image_sp == 0 || stub_src == 0 || stub_cons == 0 || image_src == 0 || image_cons == 0 || image_stage == 0 || image_join == 0 || stub_join_control == 0 || image_join_control == 0 || table_rows == 0 )); then
    verdict=H-CoverageInvalid
else
    verdict=$(grep -a 'metadata all_target_stage_rows=' "$OUT/driver.log" | tail -1 | sed -E 's/.* verdict=([^ ]+).*/\1/')
fi
print "verdict=$verdict oracle_controls=$oracle_ok image_stage=$image_stage image_join=$image_join table_rows=$table_rows filter_voice_control=${filter_stub}/${filter_image}" | tee -a "$OUT/driver.log"
exit 0
