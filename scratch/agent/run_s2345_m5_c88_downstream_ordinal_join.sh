#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2345_m5_c88_downstream_ordinal_join}
OUT="$ROOT/scratch/agent/$TAG"
WINCTL="$BUILD/winctl"

[[ "$TAG" != .* ]] || exit 2
mkdir -p "$OUT"
if [[ ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" || ! -x "$WINCTL" ]]; then
    print "ERROR: build prerequisites are missing" > "$OUT/driver.log"
    exit 3
fi

cd "$ROOT" || exit 4
PORT_PRESS=(6 11 16 21 26 31 36 41 46 51 56)
COMMON=(
    ROGUESQ_LLE_FORCE=1
    ROGUESQ_SPIN_YIELD=1
    ROGUESQ_LLE_UNGATED=1
    ROGUESQ_LLE_SOLO=1
    ROGUESQ_M5_B40_VALUE=0
    ROGUESQ_STUB_MISSING_FUNCS=1
    ROGUESQ_LOG_PHASE=1
    ROGUESQ_LOG_AUDIO_RETURN=1
    ROGUESQ_LOG_M5_TASK_CONTRACT=1
    ROGUESQ_LOG_PCM_BOUNDARY=1
    ROGUESQ_LOG_M5_HOST_BOUNDARY=1
    ROGUESQ_LOG_M5_B40_ROUTE=1
    ROGUESQ_LOG_M5_B40_WRITER=1
    ROGUESQ_LOG_M5_B40_READ=1
    ROGUESQ_LOG_M5_C88_ROUTE_FINGERPRINT=1
    ROGUESQ_LOG_M5_ROUTE_STATE=1
    ROGUESQ_LOG_M5_GATE_CONTRACT=1
    ROGUESQ_LOG_AUDIOTICK_TRACE=1
    ROGUESQ_LOG_VI_CALLERS=1
    ROGUESQ_LOG_FILTER_VOICE_AUDIT=1
    ROGUESQ_LOG_INIT_VOICE_SAMPLE=1
    ROGUESQ_LOG_M5_KEYON_CENSUS=1
    ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1
)

PIDS=()
KEYPIDS=()
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
    local i
    for (( i = 1; i <= ${#PIDS[@]}; ++i )); do
        cleanup_game "${PIDS[$i]}" "${KEYPIDS[$i]}"
    done
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
    local at
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
    local c88="$3"
    local log="$OUT/$name.log"
    (
        cd "$BUILD" || exit 2
        exec env ${=COMMON} ROGUESQ_AUDIO_UCODE="$audio" ROGUESQ_M5_C88_VALUE="$c88" ./RogueSquadron64Recomp
    ) > "$log" 2>&1 &
    local pid=$!
    local keypid=""
    PIDS+=("$pid")
    KEYPIDS+=("")
    print "${name}_pid=$pid audio=$audio c88=$c88" | tee -a "$OUT/driver.log"
    if wait_for_window "$pid"; then
        send_keys "$name" "$pid" &
        keypid=$!
        KEYPIDS[-1]="$keypid"
    else
        print "${name}_window=missing" | tee -a "$OUT/driver.log"
    fi

    local hangar=0
    local deadline=$((SECONDS + 240))
    while (( SECONDS < deadline )); do
        if grep -a -q '^\[phase\] vi_width=1024 .*origin=0x00790400' "$log" && \
           grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log"; then
            hangar=1
            print "${name}_controls=passed title=1 hangar=1; retaining_15s" | tee -a "$OUT/driver.log"
            sleep 15
            break
        fi
        if ! kill -0 "$pid" 2>/dev/null; then break; fi
        sleep 1
    done
    (( hangar )) || print "${name}_controls=failed title_or_hangar_missing" | tee -a "$OUT/driver.log"
    cleanup_game "$pid" "$keypid"
    wait "$keypid" 2>/dev/null || true
    wait "$pid" 2>/dev/null
    local rc=$?
    print "${name}_rc=$rc controls=$hangar" | tee -a "$OUT/driver.log"
}

print "arms=stub_c0,stub_c1,image_c0,image_c1 sequential; eleven-start; B40=0" | tee "$OUT/driver.log"
run_arm stub_c0 0 0
run_arm stub_c1 0 1
run_arm image_c0 1 0
run_arm image_c1 1 1

python3 - "$OUT" "$OUT/ordinal-table.tsv" "$OUT/ordinal-summary.tsv" <<'PY' | tee -a "$OUT/driver.log"
import re
import sys
from collections import defaultdict
from pathlib import Path

out_dir, table_path, summary_path = map(Path, sys.argv[1:])
token = re.compile(r"([^=\s]+)=([^\s]+)")
arms = ("stub_c0", "stub_c1", "image_c0", "image_c1")
phases = ((1024, 0x790400), (512, 0x6AB400))

def num(value):
    try:
        return int(value, 0)
    except (TypeError, ValueError):
        return 0

def parse(path):
    rows = []
    with path.open(errors="replace") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.startswith("[") or "]" not in line:
                continue
            tag, rest = line[1:].split("]", 1)
            fields = dict(token.findall(rest))
            fields["line"] = str(line_no)
            fields["tag"] = tag
            rows.append(fields)
    return rows

def phase_key(row):
    width = num(row.get("width"))
    origin = num(row.get("origin"))
    return (width, origin) if (width, origin) in phases else None

def count_tag(rows, tag, extra=None):
    return sum(r["tag"] == tag and (extra is None or extra(r)) for r in rows)

def exact(rows, tag, key, extra=None):
    return [r for r in rows if r["tag"] == tag and (num(r.get("ordinal")), num(r.get("row"))) == key and (extra is None or extra(r))]

def field_count(rows, tag, field, value):
    return sum(r["tag"] == tag and r.get(field) == value for r in rows)

header = [
    "arm", "audio", "c88", "phase", "width", "origin", "writer_seq",
    "branch_event", "branch_lhs", "branch_taken", "route_ordinal", "route_row",
    "keyon_event", "keyon_normal_tail", "keyon_table_normal_tail", "keyon_table_slot02", "keyon_table_slot00", "slot_event", "voice_event",
    "descriptor_event", "filter_event_phase", "pcm_source_event", "pcm_consumer_event",
    "pcm_same_ordinal", "task_complete", "task_dma_count", "task_source_before_consumer",
    "task_classification", "writer_stored", "controls",
]
table = [header]
summary_header = [
    "arm", "audio", "c88", "controls", "writers", "stored_nonzero", "branch_rows",
    "fallthrough_joined", "keyon_joined", "descriptor_joined", "pcm_source_joined",
    "pcm_consumer_joined", "same_ordinal_pcm_joined", "filter_phase_rows", "task_complete",
    "task_dma_rows", "task_dma_ranges", "guest_receive", "pcm_source", "pcm_consumer",
    "render_rows", "keyon_tables", "crash", "abort",
]
summary = [summary_header]

for arm in arms:
    log = out_dir / f"{arm}.log"
    rows = parse(log)
    audio = 0 if arm.startswith("stub") else 1
    c88 = 1 if arm.endswith("_c1") else 0
    branch = [r for r in rows if r["tag"] == "m5-synth-pregate" and r.get("source") == "0x80091468" and phase_key(r) is not None]
    writers = [r for r in rows if r["tag"] == "m5-b40-writer" and phase_key(r) is not None]
    keyon_tables = [r for r in rows if r["tag"] == "m5-keyon-table" and phase_key(r) is not None]
    filters = [r for r in rows if r["tag"] == "filter-voice-audit" and phase_key(r) is not None]
    controls = int(
        count_tag(rows, "vi-callers-control") > 0 and
        count_tag(rows, "filter-voice-audit-control") > 0 and
        count_tag(rows, "m5-audio-join-control") > 0 and
        count_tag(rows, "audtask-abi") > 0 and
        count_tag(rows, "audtask-dma-row") > 0 and
        count_tag(rows, "audio-sp-route", lambda r: r.get("edge") == "guest-receive") > 0 and
        count_tag(rows, "pcm-boundary-source") > 0 and
        count_tag(rows, "pcm-boundary-consumer") > 0 and
        count_tag(rows, "m5-keyon-table") > 0 and
        count_tag(rows, "phase", lambda r: num(r.get("vi_width")) == 1024 and num(r.get("origin")) == 0x790400) > 0 and
        count_tag(rows, "phase", lambda r: num(r.get("vi_width")) == 512 and num(r.get("origin")) == 0x6AB400) > 0
    )
    for width, origin in phases:
        phase_branch = [r for r in branch if phase_key(r) == (width, origin)]
        phase_writer = [r for r in writers if phase_key(r) == (width, origin)]
        writer_by_seq = {num(r.get("seq")): num(r.get("stored")) for r in phase_writer}
        phase_filter_count = sum(phase_key(r) == (width, origin) for r in filters)
        phase_tables = [r for r in keyon_tables if phase_key(r) == (width, origin)]
        table_snapshot = phase_tables[-1] if phase_tables else {}
        for branch_row in phase_branch:
            key = (num(branch_row.get("ordinal")), num(branch_row.get("row")))
            keyon = exact(rows, "m5-keyon-event", key, lambda r: phase_key(r) == (width, origin))
            keyon_audio = exact(rows, "m5-audio-event", key, lambda r: phase_key(r) == (width, origin) and r.get("kind", "").startswith("keyon-"))
            slot = exact(rows, "m5-audio-event", key, lambda r: phase_key(r) == (width, origin) and r.get("kind", "").startswith("slot"))
            voice = exact(rows, "m5-audio-event", key, lambda r: phase_key(r) == (width, origin) and "voice" in r.get("kind", ""))
            descriptor = exact(rows, "init-voice-sample", key, lambda r: phase_key(r) == (width, origin))
            joins = exact(rows, "audtask-image-join", key, lambda r: phase_key(r) == (width, origin))
            source_events = [num(r.get("source_event")) for r in joins if num(r.get("source_event")) > 0]
            consumer_events = [num(r.get("consumer_event")) for r in joins if num(r.get("consumer_event")) > 0]
            task_complete = sum(num(r.get("complete")) == 1 for r in joins)
            dma_counts = [num(r.get("dma_count")) for r in joins if r.get("dma_count") is not None]
            classification = ",".join(sorted(set(r.get("classification", "") for r in joins)))
            stored = writer_by_seq.get(num(branch_row.get("writer_seq")), -1)
            table.append([
                arm, str(audio), str(c88), "target", str(width), f"0x{origin:06X}", branch_row.get("writer_seq", ""),
                branch_row.get("event", ""), branch_row.get("lhs", ""), branch_row.get("taken", ""),
                branch_row.get("ordinal", ""), branch_row.get("row", ""), str(len(keyon) + len(keyon_audio)),
                str(max((num(r.get("normal_tail")) for r in keyon), default=0)),
                table_snapshot.get("normal_tail", ""), table_snapshot.get("slot02", ""), table_snapshot.get("slot00", ""),
                str(len(keyon) + len(keyon_audio)), str(len(slot)),
                str(len(descriptor)), str(phase_filter_count), ",".join(map(str, source_events)),
                ",".join(map(str, consumer_events)), str(bool(source_events or consumer_events)),
                str(task_complete), str(max(dma_counts, default=0)),
                str(sum(num(r.get("source_before_consumer")) == 1 for r in joins)), classification,
                str(stored), str(controls),
            ])
    phase_target_branch = [r for r in branch if phase_key(r) is not None]
    fallthrough = [r for r in phase_target_branch if num(r.get("taken")) == 0 and num(r.get("writer_seq")) > 0]
    joined_keyon = 0
    joined_desc = 0
    joined_source = 0
    joined_consumer = 0
    same_pcm = 0
    complete = 0
    for r in fallthrough:
        key = (num(r.get("ordinal")), num(r.get("row")))
        k = phase_key(r)
        joined_keyon += bool(
            exact(rows, "m5-keyon-event", key, lambda x: phase_key(x) == k) or
            exact(rows, "m5-audio-event", key, lambda x: phase_key(x) == k and (x.get("kind", "").startswith("slot") or x.get("kind", "").startswith("keyon-")))
        )
        joined_desc += bool(exact(rows, "init-voice-sample", key, lambda x: phase_key(x) == k))
        joins = exact(rows, "audtask-image-join", key, lambda x: phase_key(x) == k)
        has_source = any(num(x.get("source_event")) > 0 for x in joins)
        has_consumer = any(num(x.get("consumer_event")) > 0 for x in joins)
        joined_source += has_source
        joined_consumer += has_consumer
        same_pcm += has_source and has_consumer
        complete += sum(num(x.get("complete")) == 1 for x in joins)
    controls_counts = {
        "guest": count_tag(rows, "audio-sp-route", lambda r: r.get("edge") == "guest-receive"),
        "pcm_source": count_tag(rows, "pcm-boundary-source"),
        "pcm_consumer": count_tag(rows, "pcm-boundary-consumer"),
    }
    summary.append([
        arm, str(audio), str(c88), str(controls), str(len(writers)),
        str(sum(num(r.get("stored")) != 0 for r in writers)), str(len(phase_target_branch)),
        str(len(fallthrough)), str(joined_keyon), str(joined_desc), str(joined_source),
        str(joined_consumer), str(same_pcm), str(len(filters)), str(complete),
        str(count_tag(rows, "audtask-dma-row")), str(count_tag(rows, "audtask-dma-range")),
        str(controls_counts["guest"]), str(controls_counts["pcm_source"]), str(controls_counts["pcm_consumer"]),
        str(count_tag(rows, "audtask-image-stage-row")), str(len(keyon_tables)),
        str(count_tag(rows, "CRASH")), str(count_tag(rows, "ABORT")),
    ])

for path, data in ((table_path, table), (summary_path, summary)):
    path.write_text("\n".join("\t".join(row) for row in data) + "\n")

print("ordinal_summary")
for row in summary[1:]:
    print(" ".join(f"{key}={value}" for key, value in zip(summary_header, row)))

if not all(row[3] == "1" for row in summary[1:]):
    print("verdict=H-CoverageInvalid missing same-run positive control")
    raise SystemExit(5)

by_arm = {row[0]: row for row in summary[1:]}
pair_ok = all(
    int(by_arm[c1][5]) > int(by_arm[c0][5]) and
    int(by_arm[c1][7]) > 0 and
    int(by_arm[c1][8]) > int(by_arm[c0][8])
    for c0, c1 in (("stub_c0", "stub_c1"), ("image_c0", "image_c1"))
)
same_ordinal = all(int(by_arm[c1][12]) > int(by_arm[c0][12]) for c0, c1 in (("stub_c0", "stub_c1"), ("image_c0", "image_c1")))
if not pair_ok:
    print("verdict=H-C88TreatmentDidNotProduceQualifiedDownstreamJoin")
elif same_ordinal and all(int(by_arm[a][12]) > 0 for a in ("stub_c1", "image_c1")):
    print("verdict=H-SameOrdinalVoicePath")
elif all(int(by_arm[a][10]) > 0 and int(by_arm[a][11]) == 0 for a in ("stub_c1", "image_c1")):
    print("verdict=H-ConsumerGap")
elif all(int(by_arm[a][8]) > 0 and int(by_arm[a][10]) == 0 for a in ("stub_c1", "image_c1")):
    print("verdict=H-TaskOutputGap")
else:
    print("verdict=H-StaleOrdinalReuseOrNoQualifiedDownstreamJoin")
PY
