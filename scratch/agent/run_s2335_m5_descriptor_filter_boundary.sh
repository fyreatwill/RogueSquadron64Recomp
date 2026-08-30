#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2335_m5_descriptor_filter_boundary}
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
    ROGUESQ_LOG_INIT_VOICE_SAMPLE=1
    PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1
)

print "oracle_start" > "$OUT/driver.log"
env "$ORACLE" \
    --core "$ORACLE_CORE" --rom "$ORACLE_ROM" --video "$ORACLE_VIDEO" \
    --secs 75 \
    --watch-write 0x0:0x800000 \
    --watch-write 0x165000:0x16B000 \
    --watch-write 0x1798B0:0x179A48 \
    --watch-write 0x141AD0:0x141AF0 \
    --watch-write 0xA0F50:0xA0F54 \
    --watch-write 0x1498A:0x1498C \
    --watch-write 0x154620:0x154624 \
    --watch-write 0x155848:0x155849 \
    --watch-write 0x156A70:0x156A71 \
    --watch-write 0x157C98:0x157C99 \
    --watch-write 0x158EC0:0x158EC1 \
    --hit-cap 64 \
    --watch-pc 0x8008FFAC,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C4E8,0x8009C904,0x8009D740,0x8009D7D0,0x8009B5A8 \
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
for pc in 8008ffac 80092230 8009231c 80090b68 80090c28 8009c904 8009d740 8009d7d0 8009b5a8; do
    grep -a -E "^\[oracle\] exec-prev pc=0x$pc .* n=[1-9][0-9]*$" "$OUT/oracle.log" >/dev/null || oracle_gate=0
done
if grep -a -q '^\[oracle\] exec-prev pc=0x8009c4e8 ' "$OUT/oracle.log"; then
    requested_update="nonzero"
else
    requested_update="zero"
fi
print "oracle_rc=$oracle_rc oracle_controls=$oracle_gate requested_update_pc_0x8009c4e8=$requested_update" | tee -a "$OUT/driver.log"
grep -a -E '^\[oracle\] (done:|watch write|exec-prev pc=0x8008|exec-prev pc=0x8009|vi )' "$OUT/oracle.log" | tail -120 >> "$OUT/driver.log" || true
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
    print "init_voice_entry=$(grep -a -c '^\[init-voice-sample\]' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    print "render_stage=$(grep -a -c 'site=render-stage' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    print "render_end=$(grep -a -c 'site=render-end' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    print "keyon=$(grep -a -c '\[m5-keyon-' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    print "descriptor_payload_print=$(grep -a -c '^\[init-desc\]' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    print "filter_real=$(grep -a -c '^\[filter-voice-audit\]' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
done

python3 - "$OUT/oracle.log" "$OUT/stub.log" "$OUT/image.log" "$OUT/descriptor-boundary-table.tsv" "$OUT/descriptor-boundary-summary.tsv" <<'PY' | tee -a "$OUT/driver.log"
import re
import sys
from collections import Counter

oracle_path, stub_path, image_path, table_path, summary_path = sys.argv[1:]
token = re.compile(r"([^=\s]+)=([^\s]+)")
retail_pcs = {
    "render": "8008ffac", "descriptor": "80092230", "trigger": "8009231c",
    "keyon_sw": "80090b68", "keyon_sh": "80090c28", "requested_zero": "8009c4e8",
    "decode": "8009c904", "filter_caller": "8009d740", "filter": "8009d7d0",
    "service": "8009b5a8",
}

def num(v, default=0):
    try:
        return int(v, 0)
    except (TypeError, ValueError):
        return default

def parse(line):
    return dict(token.findall(line))

retail = Counter()
retail_watch = {}
with open(oracle_path, errors="replace") as stream:
    for line in stream:
        match = re.search(r"^\[oracle\] exec-prev pc=0x([0-9a-f]+) .* n=(\d+)$", line)
        if match:
            pc, count = match.groups()
            for name, wanted in retail_pcs.items():
                if pc == wanted:
                    retail[name] += int(count)
        match = re.search(r"^\[oracle\] watch write \[(0x[0-9a-f]+),(0x[0-9a-f]+)\): (\d+) hit", line)
        if match:
            retail_watch[match.group(1)] = int(match.group(3))

def target(width, origin):
    return (num(width) == 1024 and num(origin) == 0x790400) or (num(width) == 512 and num(origin) == 0x6AB400)

def read_arm(path, arm):
    counts = Counter()
    events = []
    stages = []
    current = {"phase": "", "width": "", "origin": ""}
    with open(path, errors="replace") as stream:
        for seq, line in enumerate(stream, 1):
            row = parse(line)
            if line.startswith("[phase]"):
                current = {"phase": row.get("phase", row.get("n", "")),
                           "width": row.get("vi_width", row.get("width", "")),
                           "origin": row.get("origin", "")}
            if line.startswith("[filter-voice-audit-control]") and row.get("kind") == "host-positive-control":
                counts["filter_control"] += 1
            if line.startswith("[m5-host-boundary-control]"):
                counts["host_boundary_control"] += 1
            if (line.startswith("[m5-port-vi-control]") and row.get("phase") == "4" and
                    num(row.get("requested_width")) == 640 and num(row.get("committed_width")) == 640 and
                    num(row.get("committed_origin")) == 0x66A500):
                counts["vi_control"] += 1
            if not target(current["width"], current["origin"]):
                continue
            if "site=render-stage" in line: counts["render_stage"] += 1
            if "site=render-end" in line: counts["render_end"] += 1
            if "[m5-keyon-" in line: counts["keyon_text"] += 1
            if line.startswith("[init-voice-sample]"):
                counts["descriptor_entry"] += 1
                events.append({"arm": arm, "class": "descriptor-entry", "phase": current["phase"],
                               "width": current["width"], "origin": current["origin"], "ordinal": "", "row": "",
                               "event": "", "site": "", "kind": "init-voice-sample", "seq": seq, **row})
            if line.startswith("[init-desc]"): counts["descriptor_payload_print"] += 1
            if line.startswith("[filter-voice-audit]"):
                counts["filter_real"] += 1
                events.append({"arm": arm, "class": "filter", "phase": row.get("phase", current["phase"]),
                               "width": row.get("width", current["width"]), "origin": row.get("origin", current["origin"]),
                               "ordinal": "", "row": "", "event": "", "site": row.get("site", ""),
                               "kind": "filter", "seq": seq, **row})
            if line.startswith("[audtask-abi]"): counts["task_abi"] += 1
            if line.startswith("[audtask-dma-row]"): counts["dma_row"] += 1
            if line.startswith("[audtask-dma-range]"): counts["dma_range"] += 1
            if line.startswith("[audio-sp-route]") and row.get("edge") == "guest-receive": counts["guest_receive"] += 1
            if line.startswith("[pcm-boundary-source]"): counts["pcm_source"] += 1
            if line.startswith("[pcm-boundary-consumer]"): counts["pcm_consumer"] += 1
            if line.startswith("[audtask-image-stage-row]"): stages.append(row)
            if line.startswith("[m5-audio-event]"):
                kind, site = row.get("kind", ""), row.get("site", "").lower()
                cls = "other"
                if kind == "keyon-w40" and site == "0x80092230":
                    cls = "descriptor-init-writer"; counts["descriptor_init_event"] += 1
                elif kind == "init-desc" and site == "0x80092230":
                    cls = "descriptor-payload-event"; counts["descriptor_payload_event"] += 1
                elif kind == "keyon-w40" and site in ("0x80090b68", "0x80090c28"):
                    cls = "keyon-writer"; counts["keyon_event"] += 1
                elif kind == "slot-sb":
                    cls = "slot-lifecycle"; counts["slot_lifecycle"] += 1
                events.append({"arm": arm, "class": cls, "phase": row.get("phase", current["phase"]),
                               "width": row.get("width", current["width"]), "origin": row.get("origin", current["origin"]),
                               "ordinal": row.get("ordinal", ""), "row": row.get("row", ""),
                               "event": row.get("event", ""), "site": row.get("site", ""), "kind": kind,
                               "seq": seq, **row})
    return counts, events, stages

arm_data = {}
all_events = []
for arm, path in (("stub", stub_path), ("image", image_path)):
    counts, events, stages = read_arm(path, arm)
    arm_data[arm] = {"counts": counts, "events": events, "stages": stages}
    all_events.extend(events)

columns = ["arm", "class", "phase", "width", "origin", "ordinal", "row", "event", "site", "kind", "seq",
           "idx", "dest", "value0", "value1", "value2", "value3", "desc", "voiceIdx", "d00", "d04"]
with open(table_path, "w") as out:
    out.write("\t".join(columns) + "\n")
    for event in all_events:
        out.write("\t".join(str(event.get(c, "")) for c in columns) + "\n")

def nonzero_stage(row):
    return num(row.get("nz")) > 0 and target(row.get("width"), row.get("origin"))

same_descriptor = 0
prior_descriptor = 0
join_rows = []
for arm in ("stub", "image"):
    data = arm_data[arm]
    descriptors = [e for e in data["events"] if e["class"] in ("descriptor-init-writer", "descriptor-payload-event")]
    for stage in data["stages"]:
        if not nonzero_stage(stage): continue
        ordinal, row, stage_event = stage.get("ordinal", ""), stage.get("row", ""), num(stage.get("event"))
        same = [e for e in descriptors if e.get("ordinal") == ordinal and e.get("row") == row]
        prior = [e for e in descriptors if e not in same]
        same_descriptor += bool(same)
        prior_descriptor += bool(prior) and not bool(same)
        join_rows.append((arm, ordinal, row, stage.get("event", ""), len(same), len(prior),
                          ";".join(f"{e.get('class')}@{num(e.get('event'))-stage_event}" for e in same),
                          ";".join(f"{e.get('class')}@{num(e.get('event'))-stage_event}" for e in prior)))

retail_required = [name for name in retail_pcs if name != "requested_zero"]
retail_controls = all(retail.get(name, 0) > 0 for name in retail_required) and retail.get("requested_zero", 0) == 0
retail_memory = retail_watch.get("0x00000000", 0) > 0 and retail_watch.get("0x00165000", 0) > 0
port_controls = all(all(arm_data[arm]["counts"][key] > 0 for key in
                        ("vi_control", "filter_control", "host_boundary_control"))
                    for arm in ("stub", "image"))
hangar = all(any(num(row.get("width")) == 512 and num(row.get("origin")) == 0x6AB400 for row in arm_data[arm]["stages"]) or
             arm_data[arm]["counts"]["render_stage"] > 0 for arm in ("stub", "image"))
target_rows = sum(sum(nonzero_stage(row) for row in arm_data[arm]["stages"]) for arm in ("stub", "image"))
init_events = sum(arm_data[arm]["counts"]["descriptor_init_event"] for arm in ("stub", "image"))
entry_rows = sum(arm_data[arm]["counts"]["descriptor_entry"] for arm in ("stub", "image"))
payload_events = sum(arm_data[arm]["counts"]["descriptor_payload_event"] for arm in ("stub", "image"))
filter_rows = sum(arm_data[arm]["counts"]["filter_real"] for arm in ("stub", "image"))
if not (retail_controls and retail_memory and port_controls):
    verdict = "H-CoverageInvalid"
elif target_rows == 0:
    verdict = "H-PortTargetStillMissing"
elif same_descriptor > 0 and filter_rows == 0:
    verdict = "H-RetailWriterIsCpuMortEdge:unclosed"
else:
    verdict = "H-RetailWriterIsImageEdge:unclosed"

with open(summary_path, "w") as out:
    out.write("metric\tvalue\n")
    metrics = {
        "retail_controls": int(retail_controls), "retail_whole_and_target_controls": int(retail_memory),
        "port_controls": int(port_controls), "hangar_control": int(hangar), "target_nonzero_stage_rows": target_rows,
        "descriptor_init_events": init_events, "descriptor_entry_rows": entry_rows,
        "descriptor_payload_events": payload_events,
        "descriptor_payload_print_rows": sum(arm_data[a]["counts"]["descriptor_payload_print"] for a in arm_data),
        "same_ordinal_descriptor_stage_joins": same_descriptor, "prior_ordinal_descriptor_stage_joins": prior_descriptor,
        "real_filter_rows": filter_rows, "verdict": verdict,
    }
    for key, value in metrics.items(): out.write(f"{key}\t{value}\n")
    for name in retail_pcs: out.write(f"retail_{name}\t{retail.get(name, 0)}\n")
    for arm in ("stub", "image"):
        for key, value in sorted(arm_data[arm]["counts"].items()): out.write(f"{arm}_{key}\t{value}\n")
    out.write("\njoin\tarm\tordinal\trow\tstage_event\tsame\tprior\tsame_events\tprior_events\n")
    for row in join_rows: out.write("\t".join(map(str, row)) + "\n")
print(f"descriptor_boundary retail={dict(retail)} init_events={init_events} entry_rows={entry_rows} payload_events={payload_events} same={same_descriptor} prior={prior_descriptor} filter={filter_rows} verdict={verdict}")
PY

sed -n '1,100p' "$OUT/descriptor-boundary-summary.tsv" >> "$OUT/driver.log"
sed -n '1,30p' "$OUT/descriptor-boundary-table.tsv" >> "$OUT/driver.log"
stub_hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/stub.log" 2>/dev/null || true)
image_hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/image.log" 2>/dev/null || true)
summary_verdict=$(awk -F '\t' '$1 == "verdict" {print $2}' "$OUT/descriptor-boundary-summary.tsv" 2>/dev/null || true)
print "controls oracle=$oracle_gate stub_hangar=$stub_hangar image_hangar=$image_hangar verdict=$summary_verdict" | tee -a "$OUT/driver.log"
print "verdict=$summary_verdict oracle_controls=$oracle_gate" | tee -a "$OUT/driver.log"
exit 0
