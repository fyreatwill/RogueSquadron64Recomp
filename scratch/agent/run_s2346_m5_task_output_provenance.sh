#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2346_m5_task_output_provenance}
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
    ROGUESQ_LOG_M5_B40_ROUTE_FINGERPRINT=1
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
    local pid="$1" keypid="$2"
    if [[ -n "$keypid" ]] && kill -0 "$keypid" 2>/dev/null; then kill -9 "$keypid" 2>/dev/null || true; fi
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        /usr/bin/pkill -KILL -P "$pid" 2>/dev/null || true
        kill -9 "$pid" 2>/dev/null || true
    fi
}
cleanup_all() {
    local i
    for (( i = 1; i <= ${#PIDS[@]}; ++i )); do cleanup_game "${PIDS[$i]}" "${KEYPIDS[$i]}"; done
}
trap cleanup_all EXIT INT TERM

raise_game() {
    local pid="$1"
    "$WINCTL" activate "$pid" >/dev/null 2>&1 || true
    /usr/bin/osascript -e "tell application \"System Events\" to set frontmost of first application process whose unix id is $pid to true" >/dev/null 2>&1 || true
}
wait_for_window() {
    local pid="$1" deadline=$((SECONDS + 30)) wid=""
    while (( SECONDS < deadline )); do
        if ! kill -0 "$pid" 2>/dev/null; then return 1; fi
        wid="$($WINCTL find "$pid" 2>/dev/null || true)"
        if [[ -n "$wid" ]]; then print "window pid=$pid id=${wid%% *}" >> "$OUT/driver.log"; return 0; fi
        sleep 1
    done
    return 1
}
send_keys() {
    local name="$1" pid="$2" previous=0 at
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
    local name="$1" audio="$2" c88="$3"
    local log="$OUT/$name.log"
    (
        cd "$BUILD" || exit 2
        exec env ${=COMMON} ROGUESQ_AUDIO_UCODE="$audio" ROGUESQ_M5_C88_VALUE="$c88" ./RogueSquadron64Recomp
    ) > "$log" 2>&1 &
    local pid=$! keypid=""
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
    local hangar=0 deadline=$((SECONDS + 240))
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

python3 - "$OUT" "$OUT/task-output-table.tsv" "$OUT/task-output-summary.tsv" <<'PY' | tee -a "$OUT/driver.log"
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
            fields["tag"] = tag
            fields["line"] = line_no
            rows.append(fields)
    return rows

def phase_key(row):
    width = num(row.get("width"))
    origin = num(row.get("origin"))
    return (width, origin) if (width, origin) in phases else None

def count(rows, tag, predicate=lambda row: True):
    return sum(row["tag"] == tag and predicate(row) for row in rows)

def joined(rows, tag, ordinal, row_no, phase):
    return [r for r in rows if r["tag"] == tag and num(r.get("ordinal")) == ordinal and
            num(r.get("row")) == row_no and phase_key(r) == phase]

def fmt(values):
    return ",".join(str(v) for v in values) if values else "-"

header = [
    "arm", "audio", "c88", "phase", "width", "origin", "route_ordinal", "route_row",
    "writer_seq", "branch_events", "branch_taken", "branch_lhs", "abi_n", "data_ptr",
    "data_size", "output_buff", "output_buff_size", "task_begin", "task_end", "task_complete",
    "dma_events", "dma_count", "dma_dest_len", "output_overlap", "image_events", "stage_nz",
    "classification", "image_source_events", "image_consumer_events", "sequence_source_events",
    "sequence_consumer_events", "sequence_source_nz", "sequence_consumer_nz", "source_before_consumer",
    "pcm_after_task", "consumer_after_task", "controls"
]
table = [header]
summary_header = [
    "arm", "audio", "c88", "controls", "writer_rows", "writer_stored_nonzero", "branch_rows",
    "fallthrough_rows", "route_rows", "output_nonzero_rows", "task_complete_rows", "dma_rows",
    "dma_ranges", "overlap_ranges", "stage_rows", "image_source_rows", "image_consumer_rows",
    "sequence_source_rows", "sequence_consumer_rows", "sequence_nonzero_rows", "pcm_source_control",
    "pcm_consumer_control", "guest_receive", "render_rows", "keyon_rows", "filter_rows", "crash", "abort"
]
summary = [summary_header]

for arm in arms:
    rows = parse(out_dir / f"{arm}.log")
    audio = int(arm.startswith("image"))
    c88 = int(arm.endswith("_c1"))
    branches = [r for r in rows if r["tag"] == "m5-synth-pregate" and
                r.get("source") == "0x80091468" and phase_key(r) in phases and
                num(r.get("writer_seq")) > 0 and num(r.get("ordinal")) != 0xFFFFFFFF]
    writers = [r for r in rows if r["tag"] == "m5-b40-writer" and phase_key(r) in phases]
    controls = int(
        count(rows, "vi-callers-control") > 0 and
        count(rows, "filter-voice-audit-control") > 0 and
        count(rows, "m5-audio-join-control") > 0 and
        count(rows, "audtask-abi") > 0 and
        count(rows, "audtask-dma-row") > 0 and
        count(rows, "audio-sp-route", lambda r: r.get("edge") == "guest-receive") > 0 and
        count(rows, "pcm-boundary-source") > 0 and
        count(rows, "pcm-boundary-consumer") > 0 and
        count(rows, "m5-keyon-table") > 0 and
        count(rows, "phase", lambda r: num(r.get("vi_width")) == 1024 and num(r.get("origin")) == 0x790400) > 0 and
        count(rows, "phase", lambda r: num(r.get("vi_width")) == 512 and num(r.get("origin")) == 0x6AB400) > 0
    )
    abi = {num(r.get("n")): r for r in rows if r["tag"] == "audtask-abi"}
    tasks = {num(r.get("n")): r for r in rows if r["tag"] == "audtask-join" and phase_key(r) in phases}
    dma_ranges = [r for r in rows if r["tag"] == "audtask-dma-range"]
    image_rows = [r for r in rows if r["tag"] == "audtask-image-join" and phase_key(r) in phases]
    pcm = [r for r in rows if r["tag"] == "audio-join-pcm" and phase_key(r) in phases]
    pcm_by_n = defaultdict(list)
    for r in pcm:
        pcm_by_n[num(r.get("n"))].append(r)
    route_keys = sorted({(phase_key(r), num(r.get("ordinal")), num(r.get("row"))) for r in branches})
    writer_by_seq = {num(r.get("seq")): num(r.get("stored")) for r in writers}
    output_rows = complete_rows = overlap_rows = stage_rows = image_source_rows = image_consumer_rows = 0
    sequence_source_rows = sequence_consumer_rows = sequence_nonzero_rows = 0
    for phase, ordinal, row_no in route_keys:
        br = [r for r in branches if phase_key(r) == phase and num(r.get("ordinal")) == ordinal and num(r.get("row")) == row_no]
        image = joined(rows, "audtask-image-join", ordinal, row_no, phase)
        task_candidates = []
        for image_row in image:
            stage_event = num(image_row.get("stage_event"))
            task_candidates.extend(
                task for task in tasks.values()
                if num(task.get("begin")) <= stage_event <= num(task.get("end"))
            )
        if task_candidates:
            task = max(task_candidates, key=lambda candidate: sum(candidate is other for other in task_candidates))
            task_n = num(task.get("n"))
        elif ordinal in tasks:
            task = tasks[ordinal]
            task_n = ordinal
        else:
            task = {}
            task_n = -1
        a = abi.get(task_n, {})
        ranges = [r for r in dma_ranges if num(r.get("n")) == task_n and phase_key(r) == phase]
        pcm_seq = pcm_by_n.get(task_n, [])
        sources = [r for r in image if num(r.get("source_event")) > 0]
        consumers = [r for r in image if num(r.get("consumer_event")) > 0]
        seq_sources = [r for r in pcm_seq if r.get("kind") == "source"]
        seq_consumers = [r for r in pcm_seq if r.get("kind") == "consumer"]
        out_nonzero = num(a.get("output_buff")) != 0 or num(a.get("output_buff_size")) != 0
        output_rows += out_nonzero
        complete_rows += num(task.get("exit")) == 1
        overlap_rows += sum(num(r.get("output_overlap")) != 0 for r in ranges)
        stage_rows += len(image)
        image_source_rows += bool(sources)
        image_consumer_rows += bool(consumers)
        sequence_source_rows += bool(seq_sources)
        sequence_consumer_rows += bool(seq_consumers)
        sequence_nonzero_rows += bool([r for r in seq_sources + seq_consumers if num(r.get("nz")) != 0])
        table.append([
            arm, str(audio), str(c88), "target", str(phase[0]), f"0x{phase[1]:06X}", str(ordinal), str(row_no),
            fmt(sorted({num(r.get("writer_seq")) for r in br})), fmt([r.get("event", "") for r in br]),
            fmt(sorted({num(r.get("taken")) for r in br})), fmt(sorted({r.get("lhs", "") for r in br})),
            str(task_n), a.get("data_ptr", "-"), a.get("data_size", "-"), a.get("output_buff", "-"),
            a.get("output_buff_size", "-"), task.get("begin", "-"), task.get("end", "-"), str(num(task.get("exit")) == 1),
            fmt([r.get("event", "") for r in ranges]), str(len(ranges)),
            fmt([f"{r.get('dram', '-')}/{r.get('len', '-')}" for r in ranges]),
            fmt(sorted({num(r.get("output_overlap")) for r in ranges})),
            fmt([r.get("stage_event", "") for r in image]), fmt(sorted({num(r.get("stage_nz")) for r in image})),
            fmt(sorted({r.get("classification", "-") for r in image})),
            fmt([r.get("source_event", "") for r in sources]), fmt([r.get("consumer_event", "") for r in consumers]),
            fmt([r.get("event", "") for r in seq_sources]), fmt([r.get("event", "") for r in seq_consumers]),
            fmt(sorted({num(r.get("nz")) for r in seq_sources})), fmt(sorted({num(r.get("nz")) for r in seq_consumers})),
            fmt(sorted({num(r.get("source_before_consumer")) for r in image})), task.get("pcm_after_task", "-"),
            task.get("consumer_after_task", "-"), str(controls)
        ])
    phase_branches = [r for r in branches if phase_key(r) in phases]
    fallthrough = sum(num(r.get("taken")) == 0 for r in phase_branches)
    summary.append([
        arm, str(audio), str(c88), str(controls), str(len(writers)), str(sum(num(r.get("stored")) != 0 for r in writers)),
        str(len(phase_branches)), str(fallthrough), str(len(route_keys)), str(output_rows), str(complete_rows),
        str(count(rows, "audtask-dma-row")), str(len(dma_ranges)), str(overlap_rows), str(stage_rows),
        str(image_source_rows), str(image_consumer_rows), str(sequence_source_rows), str(sequence_consumer_rows),
        str(sequence_nonzero_rows), str(count(rows, "pcm-boundary-source")), str(count(rows, "pcm-boundary-consumer")),
        str(count(rows, "audio-sp-route", lambda r: r.get("edge") == "guest-receive")),
        str(count(rows, "audtask-image-stage-row")), str(count(rows, "m5-keyon-table")),
        str(count(rows, "filter-voice-audit")), str(count(rows, "CRASH")), str(count(rows, "ABORT"))
    ])

for path, data in ((table_path, table), (summary_path, summary)):
    path.write_text("\n".join("\t".join(row) for row in data) + "\n")

print("task_output_summary")
for row in summary[1:]:
    print(" ".join(f"{key}={value}" for key, value in zip(summary_header, row)))

if not all(row[3] == "1" for row in summary[1:]):
    print("verdict=H-CoverageInvalid missing same-run positive control")
    raise SystemExit(5)

by_arm = {row[0]: row for row in summary[1:]}
if not all(int(by_arm[c1][7]) > int(by_arm[c0][7]) for c0, c1 in (("stub_c0", "stub_c1"), ("image_c0", "image_c1"))):
    print("verdict=H-C88TreatmentDidNotProduceQualifiedFallthrough")
elif all(int(by_arm[a][9]) == 0 for a in ("stub_c1", "image_c1")):
    print("verdict=H-OutputMetadataWriterAbsent")
elif all(int(by_arm[a][13]) == 0 and int(by_arm[a][9]) > 0 for a in ("stub_c1", "image_c1")):
    print("verdict=H-DmaRangeDoesNotPublish")
elif all(int(by_arm[a][17]) > 0 and int(by_arm[a][18]) == 0 for a in ("stub_c1", "image_c1")):
    print("verdict=H-PcmPublicationNoConsumer")
elif any(int(by_arm[a][19]) > 0 and int(by_arm[a][15]) == 0 for a in ("stub_c1", "image_c1")):
    print("verdict=H-OrdinalJoinMisclassified")
else:
    print("verdict=H-TaskOutputGapUnresolved")
PY
