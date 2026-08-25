#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2333_m5_voice_path_boundary}
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
    PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1
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
    --watch-write 0x155848:0x155849 \
    --watch-write 0x156A70:0x156A71 \
    --watch-write 0x157C98:0x157C99 \
    --watch-write 0x158EC0:0x158EC1 \
    --hit-cap 64 \
    --watch-pc 0x8008FFAC,0x8009C4E8,0x8009C904,0x8009D7D0,0x8009B5A8 \
    --pc-phase-log-width 0x006AB400:512 \
    --vi-trace --status-poll --press "$PRESS" > "$OUT/oracle.log" 2>&1
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
for pc in 8008ffac 8009c904 8009d7d0 8009b5a8; do
    grep -a -E "^\[oracle\] exec-prev pc=0x$pc .* n=[1-9][0-9]*$" "$OUT/oracle.log" >/dev/null || oracle_gate=0
done
if grep -a -q '^\[oracle\] exec-prev pc=0x8009c4e8 ' "$OUT/oracle.log"; then
    requested_update="nonzero"
else
    requested_update="zero"
fi
print "oracle_rc=$oracle_rc oracle_controls=$oracle_gate requested_update_pc_0x8009c4e8=$requested_update" | tee -a "$OUT/driver.log"
grep -a -E '^\[oracle\] (done:|watch write|exec-prev pc=0x8008|exec-prev pc=0x8009|vi )' "$OUT/oracle.log" | tail -100 >> "$OUT/driver.log" || true
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
trap 'cleanup_game "$STUB_PID" "$STUB_KEY_PID"; cleanup_game "$IMAGE_PID" "$IMAGE_KEY_PID"' EXIT INT TERM

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
    if [[ "$name" == stub ]]; then STUB_PID="$pid"; else IMAGE_PID="$pid"; fi
    print "${name}_pid=$pid audio=$audio drain_tick=1" | tee -a "$OUT/driver.log"
    if wait_for_window "$pid"; then
        send_keys "$name" "$pid" & keypid=$!
        if [[ "$name" == stub ]]; then STUB_KEY_PID="$keypid"; else IMAGE_KEY_PID="$keypid"; fi
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
    for marker in '[vi-callers-control]' '[filter-voice-audit-control]' '[audtask-abi]' '[audtask-dma-row]' '[audtask-dma-range]' '[audtask-image-stage-row]' '[audtask-image-join]' '[audtask-join]' '[audio-sp-route] edge=guest-receive' '[pcm-boundary-source]' '[pcm-boundary-consumer]' '[m5-audio-event]' '[CRASH]' '[ABORT]'; do
        print "$marker=$(grep -a -F -c "$marker" "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    done
    print "render_stage=$(grep -a -c 'site=render-stage' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    print "render_end=$(grep -a -c 'site=render-end' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    print "keyon=$(grep -a -c '\[m5-keyon-' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    print "descriptor=$(grep -a -c '^\[init-desc\]' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    print "filter_real=$(grep -a -c '^\[filter-voice-audit\]' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
done

python3 - "$OUT/oracle.log" "$OUT/stub.log" "$OUT/image.log" "$OUT/voice-path-table.tsv" "$OUT/voice-path-summary.tsv" <<'PY' | tee -a "$OUT/driver.log"
import re
import sys
from collections import Counter

oracle_path, stub_path, image_path, table_path, summary_path = sys.argv[1:]
token = re.compile(r"([^=\s]+)=([^\s]+)")
watched = {
    "retail_render": "8008ffac",
    "retail_update_requested": "8009c4e8",
    "retail_decode": "8009c904",
    "retail_filter": "8009d7d0",
    "retail_service": "8009b5a8",
}

def number(value, default=0):
    if isinstance(value, int):
        return value
    try:
        return int(value, 0)
    except (TypeError, ValueError):
        return default

def parse(line):
    return dict(token.findall(line))

def is_target(row):
    return (number(row.get("width", row.get("vi_width"))) == 512 and
            number(row.get("origin")) == 0x6AB400)

retail = Counter()
retail_watch = {}
with open(oracle_path, errors="replace") as stream:
    for line in stream:
        match = re.search(r"^\[oracle\] exec-prev pc=0x([0-9a-f]+) .* n=(\d+)$", line)
        if match:
            pc, count = match.groups()
            for name, wanted in watched.items():
                if pc == wanted:
                    retail[name] += int(count)
        match = re.search(r"^\[oracle\] watch write \[(0x[0-9a-f]+),(0x[0-9a-f]+)\): (\d+) hit", line)
        if match:
            retail_watch[match.group(1)] = int(match.group(3))

def read_arm(path, arm):
    counts = Counter()
    stages = []
    lifecycle = []
    current_target = False
    with open(path, errors="replace") as stream:
        for seq, line in enumerate(stream, 1):
            tag = line.split()[0] if line.split() else ""
            row = parse(line)
            row.update(tag=tag, seq=seq, arm=arm)
            if row.get("width") and row.get("origin"):
                current_target = is_target(row)
            in_target = is_target(row) or current_target
            if "site=render-stage" in line and in_target: counts["render_stage"] += 1
            if "site=render-end" in line and in_target: counts["render_end"] += 1
            if "[m5-keyon-" in line and in_target: counts["keyon"] += 1
            if "init-desc" in line and in_target: counts["descriptor"] += 1
            if tag == "[filter-voice-audit]" and in_target: counts["filter_real"] += 1
            if tag == "[filter-voice-audit-control]" and "kind=host-positive-control" in line:
                counts["filter_control"] += 1
            if tag == "[audtask-abi]" and in_target: counts["task_abi"] += 1
            if tag == "[audtask-dma-row]" and in_target: counts["dma"] += 1
            if tag == "[audio-sp-route]" and row.get("edge") == "guest-receive" and in_target:
                counts["guest_receive"] += 1
            if tag == "[audtask-image-stage-row]":
                stages.append(row)
                if in_target and number(row.get("nz")) > 0: counts["stage_nonzero"] += 1
            if tag == "[audtask-image-join]" and in_target: counts["image_join"] += 1
            if tag == "[audtask-join]" and in_target: counts["task_join"] += 1
            if tag == "[pcm-boundary-source]" and in_target: counts["pcm_source"] += 1
            if tag == "[pcm-boundary-consumer]" and in_target: counts["pcm_consumer"] += 1
            if tag == "[m5-audio-event]":
                lifecycle.append(row)
                counts["lifecycle"] += 1
    target_stages = [row for row in stages if is_target(row) and number(row.get("nz")) > 0]
    target_stages.sort(key=lambda row: number(row.get("event")))
    rows = []
    for stage in target_stages:
        ordinal = stage.get("ordinal", "")
        stage_row = stage.get("row", "")
        stage_event = number(stage.get("event"))
        same = [event for event in lifecycle if event.get("ordinal") == ordinal and event.get("row") == stage_row]
        prior = [event for event in lifecycle
                 if event.get("ordinal") != ordinal or event.get("row") != stage_row]
        post = [event for event in same if number(event.get("event")) > stage_event]
        rows.append({
            "arm": arm, "phase": stage.get("phase", ""), "width": stage.get("width", ""),
            "origin": stage.get("origin", ""), "ordinal": ordinal, "row": stage_row,
            "stage": stage.get("stage", ""), "stage_event": stage.get("event", ""),
            "dest": stage.get("dest", ""), "len": stage.get("len", ""),
            "render_stage": counts["render_stage"], "render_end": counts["render_end"],
            "keyon": counts["keyon"], "descriptor": counts["descriptor"],
            "filter_control": counts["filter_control"], "filter_real": counts["filter_real"],
            "task_abi": counts["task_abi"], "dma": counts["dma"],
            "guest_receive": counts["guest_receive"], "task_join": counts["task_join"],
            "image_join": counts["image_join"], "pcm_source": counts["pcm_source"],
            "pcm_consumer": counts["pcm_consumer"], "lifecycle": len(same),
            "post_lifecycle": len(post), "prior_lifecycle": len(prior),
            "same_events": ";".join(f"{event.get('kind','')}@{number(event.get('event')) - stage_event}" for event in same),
            "prior_events": ";".join(f"{event.get('kind','')}@{number(event.get('event')) - stage_event}" for event in prior),
        })
    return rows, counts

all_rows = []
arm_data = {}
for arm, path in (("stub", stub_path), ("image", image_path)):
    rows, counts = read_arm(path, arm)
    all_rows.extend(rows)
    arm_data[arm] = counts

base_columns = [
    "arm", "phase", "width", "origin", "ordinal", "row", "stage", "stage_event", "dest", "len",
    "render_stage", "render_end", "keyon", "descriptor", "filter_control", "filter_real",
    "task_abi", "dma", "guest_receive", "task_join", "image_join", "pcm_source", "pcm_consumer",
    "lifecycle", "post_lifecycle", "prior_lifecycle", "same_events", "prior_events",
]
retail_columns = list(watched)
with open(table_path, "w") as out:
    out.write("\t".join(base_columns + retail_columns) + "\n")
    for row in all_rows:
        out.write("\t".join(str(row.get(column, "")) for column in base_columns + retail_columns) + "\n")

retail_controls = all(retail.get(name, 0) > 0 for name in watched if name != "retail_update_requested")
retail_memory = retail_watch.get("0x00000000", 0) > 0 and retail_watch.get("0x00165000", 0) > 0
port_controls = all(
    arm_data[arm]["task_abi"] > 0 and arm_data[arm]["dma"] > 0 and
    arm_data[arm]["guest_receive"] > 0 and arm_data[arm]["filter_control"] > 0
    for arm in ("stub", "image")
)
render_total = sum(arm_data[arm]["render_stage"] for arm in arm_data)
keyon_total = sum(arm_data[arm]["keyon"] for arm in arm_data)
descriptor_total = sum(arm_data[arm]["descriptor"] for arm in arm_data)
filter_total = sum(arm_data[arm]["filter_real"] for arm in arm_data)
post_total = sum(number(row.get("post_lifecycle")) > 0 for row in all_rows)
prior_total = sum(number(row.get("prior_lifecycle")) > 0 for row in all_rows)
if not (retail_controls and retail_memory and port_controls and all_rows):
    verdict = "H-CoverageInvalid"
elif render_total == 0:
    verdict = "H-UpstreamVoiceAbsent"
elif (render_total > 0 and keyon_total > 0 and descriptor_total > 0 and
      filter_total == 0 and post_total == 0):
    verdict = "H-FilterPathGated"
elif filter_total > 0 and post_total == 0 and prior_total > 0:
    verdict = "H-PriorOrdinalReuse"
else:
    verdict = "H-VoiceBoundaryUnresolved"

with open(summary_path, "w") as out:
    out.write("metric\tvalue\n")
    for name, value in (
        ("retail_controls", int(retail_controls)),
        ("retail_whole_and_target_controls", int(retail_memory)),
        ("port_controls", int(port_controls)),
        ("target_stage_rows", len(all_rows)),
        ("render_stage_rows", render_total),
        ("keyon_rows", keyon_total),
        ("descriptor_rows", descriptor_total),
        ("real_filter_rows", filter_total),
        ("rows_with_post_lifecycle", post_total),
        ("rows_with_prior_lifecycle", prior_total),
        ("verdict", verdict),
    ):
        out.write(f"{name}\t{value}\n")
    for name in watched:
        out.write(f"{name}\t{retail.get(name, 0)}\n")
print(f"voice_path target_rows={len(all_rows)} retail={dict(retail)} render_stage={render_total} keyon={keyon_total} real_filter={filter_total} post={post_total} prior={prior_total} verdict={verdict}")
PY

sed -n '1,80p' "$OUT/voice-path-summary.tsv" >> "$OUT/driver.log"
sed -n '1,20p' "$OUT/voice-path-table.tsv" >> "$OUT/driver.log"
stub_hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/stub.log" 2>/dev/null || true)
image_hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/image.log" 2>/dev/null || true)
summary_verdict=$(awk -F '\t' '$1 == "verdict" {print $2}' "$OUT/voice-path-summary.tsv" 2>/dev/null || true)
table_rows=$(awk -F '\t' 'NR > 1 {n++} END {print n+0}' "$OUT/voice-path-table.tsv" 2>/dev/null || true)
print "controls oracle=$oracle_gate stub_hangar=$stub_hangar image_hangar=$image_hangar table=$table_rows verdict=$summary_verdict" | tee -a "$OUT/driver.log"
if (( stub_hangar == 0 || image_hangar == 0 )); then
    print "verdict=H-CoverageInvalid port_hangar=0" | tee -a "$OUT/driver.log"
    exit 6
fi
print "verdict=$summary_verdict oracle_controls=$oracle_gate" | tee -a "$OUT/driver.log"
exit 0
