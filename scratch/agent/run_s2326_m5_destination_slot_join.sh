#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2326_m5_destination_slot_join}
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
        '[vi-callers-control]' '[filter-voice-audit-control]' '[audtask-dispatch]' \
        '[audtask-abi]' '[audtask-dma-row]' '[audtask-dma-range]' \
        '[audtask-image-stage-row]' '[audtask-image-join]' '[audtask-join]' \
        '[audtask-join-range]' '[audio-return]' '[m5-gate]' '[slot-alloc]' \
        '[slot-byte]' '[slot-sb]' '[init-desc]' '[keyon-w40]' \
        '[filter-voice-audit]' '[m5-keyon-table]' '[m5-keyon-event]' \
        '[m5-keyon-transfer]' '[pcm-boundary-source]' '[pcm-boundary-consumer]' \
        '[m5-b40-route]' '[m5-route-state]' '[CRASH]' '[ABORT]'; do
        print "$marker=$(grep -a -F -c "$marker" "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    done
    print "title=$(grep -a -c '^\[phase\] vi_width=1024 .*origin=0x00790400' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    print "hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
}
emit_counts stub
emit_counts image

python3 - "$OUT/image.log" "$OUT/image-downstream-events.tsv" "$OUT/image-downstream-raw.tsv" <<'PY'
import re
import sys
from collections import Counter, defaultdict

log_path, table_path, raw_path = sys.argv[1:]
kv_re = re.compile(r'([^=\s]+)=([^\s]+)')

def parse_int(value, default=0):
    if value is None:
        return default
    try:
        return int(value, 0)
    except ValueError:
        try:
            return int(value)
        except ValueError:
            return default

def tokens(line):
    parts = line.split()
    return parts[0] if parts else "", dict(kv_re.findall(line))

phase = {"phase": "", "width": "", "origin": ""}
arm = ""
stages = []
joins = []
downstream = []

with open(log_path, "r", errors="replace") as stream:
    for seq, line in enumerate(stream, 1):
        tag, fields = tokens(line)
        if tag == "[phase]":
            if "vi_width" in fields and "origin" in fields:
                phase = {
                    "phase": fields.get("phase", ""),
                    "width": fields.get("vi_width", ""),
                    "origin": fields.get("origin", ""),
                }
        if "arm" in fields:
            arm = fields["arm"]
        if "phase" in fields:
            phase["phase"] = fields["phase"]
        if "width" in fields:
            phase["width"] = fields["width"]
        if "origin" in fields:
            phase["origin"] = fields["origin"]
        if "vi_width" in fields:
            phase["width"] = fields["vi_width"]
        if tag == "[audtask-image-stage-row]":
            stages.append({"seq": seq, "arm": fields.get("arm", arm), **fields})
        elif tag == "[audtask-image-join]":
            joins.append({"seq": seq, "arm": fields.get("arm", arm), **fields})
        else:
            kind = None
            if tag == "[avf-gate]":
                site = fields.get("site", "")
                if site in {"slot-alloc", "slot-byte", "slot-sb", "render-stage", "render-end", "rekey", "slot-ret", "attack-jal", "cursor"}:
                    kind = site
            elif tag == "[keyon-w40]":
                kind = "keyon-w40"
            elif tag == "[init-desc]":
                kind = "init-desc"
            elif tag == "[filter-voice-audit]":
                kind = "filter-voice-audit"
            elif tag.startswith("[m5-keyon-"):
                kind = tag[1:-1]
            if kind:
                downstream.append({"seq": seq, "arm": fields.get("arm", ""), "arm_explicit": "arm" in fields, "kind": kind, **phase, **fields})

def norm(value):
    return value.lower().replace("0x", "") if value else ""

target_stages = [
    stage for stage in stages
    if parse_int(stage.get("width")) == 512
    and parse_int(stage.get("origin")) == 0x6AB400
    and parse_int(stage.get("nz")) > 0
    and parse_int(stage.get("stage")) in (2, 3)
]
target_stages.sort(key=lambda row: row["seq"])
target_keys = {(row.get("arm", ""), row.get("ordinal", ""), row.get("row", ""), norm(row.get("dest", ""))) for row in target_stages}

def join_for(stage):
    key = (stage.get("arm", ""), stage.get("ordinal", ""), stage.get("row", ""), norm(stage.get("dest", "")))
    matches = [row for row in joins if (row.get("arm", ""), row.get("ordinal", ""), row.get("row", ""), norm(row.get("dest", ""))) == key]
    return max(matches, key=lambda row: row["seq"]) if matches else {}

def same_scope(left, right):
    return ((not right.get("arm_explicit", False) or left.get("arm", "") == right.get("arm", "")) and
            parse_int(left.get("phase")) == parse_int(right.get("phase")) and
            parse_int(left.get("width")) == parse_int(right.get("width")) and
            parse_int(left.get("origin")) == parse_int(right.get("origin")))

def event_preview(event):
    order = ("kind", "site", "func", "idx", "byte", "old", "new", "dest", "base", "desc", "d00", "d04", "d08", "d0c", "d10", "d14", "d18")
    return ",".join(f"{key}={event[key]}" for key in order if key in event)

def m5_keyon_count(counter):
    return sum(value for kind, value in counter.items() if kind.startswith("m5-keyon-"))

rows = []
raw_rows = []
for index, stage in enumerate(target_stages):
    next_seq = len(stages) + 1
    for later in target_stages[index + 1:]:
        if same_scope(stage, later):
            next_seq = later["seq"]
            break
    task_stages = [candidate for candidate in target_stages if
                   candidate.get("arm", "") == stage.get("arm", "") and
                   candidate.get("phase", "") == stage.get("phase", "") and
                   candidate.get("width", "") == stage.get("width", "") and
                   candidate.get("origin", "") == stage.get("origin", "") and
                   candidate.get("ordinal", "") == stage.get("ordinal", "") and
                   candidate.get("row", "") == stage.get("row", "")]
    task_start = min(candidate["seq"] for candidate in task_stages)
    task_end = max(candidate["seq"] for candidate in task_stages)
    pre_window = [event for event in downstream if event["seq"] >= task_start - 256 and event["seq"] < task_start and same_scope(stage, event)]
    post_window = [event for event in downstream if event["seq"] > task_end and event["seq"] < next_seq and same_scope(stage, event)]
    counts = Counter(event["kind"] for event in post_window)
    pre_counts = Counter(event["kind"] for event in pre_window)
    previews = defaultdict(list)
    for event in post_window:
        if len(previews[event["kind"]]) < 8:
            previews[event["kind"]].append(f"d{event['seq'] - stage['seq']}:{event_preview(event)}")
    pre_previews = defaultdict(list)
    for event in pre_window:
        if len(pre_previews[event["kind"]]) < 8:
            pre_previews[event["kind"]].append(f"d{event['seq'] - stage['seq']}:{event_preview(event)}")
    join = join_for(stage)
    slot_bytes = [f"idx={event.get('idx','')}:{event.get('byte','')}" for event in post_window if event["kind"] == "slot-byte"]
    pre_slot_bytes = [f"idx={event.get('idx','')}:{event.get('byte','')}" for event in pre_window if event["kind"] == "slot-byte"]
    row = [
        stage.get("arm", ""), stage.get("phase", ""), stage.get("width", ""), stage.get("origin", ""),
        stage.get("ordinal", ""), stage.get("row", ""), stage.get("stage", ""), stage["seq"], next_seq,
        stage.get("event", ""), stage.get("dest", ""), stage.get("len", ""), stage.get("fnv", ""), stage.get("nz", ""),
        join.get("classification", ""), join.get("source_event", ""), join.get("consumer_event", ""),
        str(counts.get("slot-alloc", 0)), str(counts.get("slot-byte", 0)), str(counts.get("slot-sb", 0)),
        str(counts.get("keyon-w40", 0)), str(counts.get("init-desc", 0)), str(counts.get("filter-voice-audit", 0)),
        str(m5_keyon_count(counts)),
        ";".join(slot_bytes[:16]),
        "|".join(f"{kind}=[{' ; '.join(previews[kind])}]" for kind in sorted(previews)),
        str(pre_counts.get("slot-alloc", 0)), str(pre_counts.get("slot-byte", 0)), str(pre_counts.get("slot-sb", 0)),
        str(pre_counts.get("keyon-w40", 0)), str(pre_counts.get("init-desc", 0)), str(pre_counts.get("filter-voice-audit", 0)),
        str(m5_keyon_count(pre_counts)),
        ";".join(pre_slot_bytes[:16]),
        "|".join(f"{kind}=[{' ; '.join(pre_previews[kind])}]" for kind in sorted(pre_previews)),
    ]
    rows.append(row)

    for event in pre_window + post_window:
        raw_rows.append([
            event["seq"], stage.get("arm", ""), stage.get("phase", ""), stage.get("width", ""), stage.get("origin", ""),
            stage.get("ordinal", ""), stage.get("row", ""), stage.get("dest", ""), event["seq"] - stage["seq"],
            "pre" if event["seq"] < task_start else "post", event["kind"], event.get("site", ""), event.get("func", ""), event.get("idx", ""), event.get("byte", ""),
            event.get("old", ""), event.get("new", ""), event.get("dest", ""), event.get("base", ""),
            event.get("desc", ""), event_preview(event),
        ])

header = [
    "arm", "phase", "width", "origin", "ordinal", "row", "stage", "stage_seq", "next_stage_seq", "stage_event",
    "dest", "len", "stage_fnv", "stage_nz", "classification", "source_event", "consumer_event", "slot_alloc_n",
    "slot_byte_n", "slot_sb_n", "keyon_w40_n", "init_desc_n", "filter_voice_n", "m5_keyon_n", "slot_bytes",
    "downstream_preview", "pre_slot_alloc_n", "pre_slot_byte_n", "pre_slot_sb_n", "pre_keyon_w40_n", "pre_init_desc_n",
    "pre_filter_voice_n", "pre_m5_keyon_n", "pre_slot_bytes", "pre_downstream_preview",
]
with open(table_path, "w") as out:
    out.write("\t".join(header) + "\n")
    for row in rows:
        out.write("\t".join(str(value) for value in row) + "\n")

raw_header = [
    "event_seq", "arm", "phase", "width", "origin", "ordinal", "row", "stage_dest", "delta", "position", "kind", "site",
    "func", "idx", "byte", "old", "new", "event_dest", "base", "desc", "fields",
]
with open(raw_path, "w") as out:
    out.write("\t".join(raw_header) + "\n")
    for row in raw_rows:
        out.write("\t".join(str(value) for value in row) + "\n")

dest_summary = defaultdict(lambda: Counter())
for row in rows:
    dest = row[10]
    summary = dest_summary[dest]
    summary["rows"] += 1
    summary["stage_nz"] += parse_int(row[13]) > 0
    for column in (17, 18, 19, 20, 21, 22, 23):
        summary[header[column]] += parse_int(row[column])
with open(table_path.replace("events.tsv", "summary.tsv"), "w") as out:
    out.write("dest\trows\tstage_nz_rows\tslot_alloc_n\tslot_byte_n\tslot_sb_n\tkeyon_w40_n\tinit_desc_n\tfilter_voice_n\tm5_keyon_n\n")
    for dest in sorted(dest_summary):
        summary = dest_summary[dest]
        out.write("\t".join([
            dest, str(summary["rows"]), str(summary["stage_nz"]), str(summary["slot_alloc_n"]),
            str(summary["slot_byte_n"]), str(summary["slot_sb_n"]), str(summary["keyon_w40_n"]),
            str(summary["init_desc_n"]), str(summary["filter_voice_n"]), str(summary["m5_keyon_n"]),
        ]) + "\n")
print(f"target_stage_rows={len(target_stages)} downstream_events={len(raw_rows)} destinations={len(dest_summary)}")
PY

sed -n '1,120p' "$OUT/image-downstream-summary.tsv" >> "$OUT/driver.log"
sed -n '1,160p' "$OUT/image-downstream-events.tsv" >> "$OUT/driver.log"

stub_hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/stub.log" 2>/dev/null || true)
image_hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/image.log" 2>/dev/null || true)
stub_vi_control=$(grep -a -c '^\[vi-callers-control\]' "$OUT/stub.log" 2>/dev/null || true)
stub_task_control=$(grep -a -c '^\[audtask-abi\]' "$OUT/stub.log" 2>/dev/null || true)
image_vi_control=$(grep -a -c '^\[vi-callers-control\]' "$OUT/image.log" 2>/dev/null || true)
image_task_control=$(grep -a -c '^\[audtask-abi\]' "$OUT/image.log" 2>/dev/null || true)
stub_controls=0
image_controls=0
if (( stub_vi_control > 0 && stub_task_control > 0 )); then stub_controls=1; fi
if (( image_vi_control > 0 && image_task_control > 0 )); then image_controls=1; fi
stub_filter_control=$(grep -a -c '^\[filter-voice-audit-control\]' "$OUT/stub.log" 2>/dev/null || true)
image_filter_control=$(grep -a -c '^\[filter-voice-audit-control\]' "$OUT/image.log" 2>/dev/null || true)
target_stage_rows=$(awk -F '\t' 'NR>1 {n++} END {print n+0}' "$OUT/image-downstream-events.tsv")
target_contract_rows=$(awk -F '\t' 'NR>1 && ($18+$19+$20+$21+$22+$24)>0 {n++} END {print n+0}' "$OUT/image-downstream-events.tsv")
destinations=$(awk -F '\t' 'NR>1 {n++} END {print n+0}' "$OUT/image-downstream-summary.tsv")
print "table target_stage_rows=$target_stage_rows contract_rows=$target_contract_rows destinations=$destinations" | tee -a "$OUT/driver.log"
print "instrument_controls stub=$stub_controls image=$image_controls oracle=$oracle_gate vi_stub=$stub_vi_control task_stub=$stub_task_control vi_image=$image_vi_control task_image=$image_task_control filter_control_stub=$stub_filter_control filter_control_image=$image_filter_control" | tee -a "$OUT/driver.log"

if (( oracle_gate == 0 || stub_hangar == 0 || image_hangar == 0 || stub_controls == 0 || image_controls == 0 || target_stage_rows == 0 )); then
    verdict=H-CoverageInvalid
elif (( target_contract_rows == 0 )); then
    verdict=H-Missing-Descriptor-Contract
elif (( destinations > 1 && target_contract_rows < target_stage_rows )); then
    verdict=H-Destination-Role-Skew
else
    verdict=H-Destination-Is-Slot-Input
fi
print "verdict=$verdict oracle_controls=$oracle_gate stub_hangar=$stub_hangar image_hangar=$image_hangar stub_instrument_controls=$stub_controls image_instrument_controls=$image_controls target_stage_rows=$target_stage_rows target_contract_rows=$target_contract_rows destinations=$destinations" | tee -a "$OUT/driver.log"
exit 0
