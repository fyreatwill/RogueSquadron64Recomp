#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2347_m5_output_writer_provenance}
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
    local name="$1" audio="$2" c88="$3" log="$OUT/$1.log"
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

python3 - "$ROOT/scratch/agent/s2347_m5_output_writer_oracle.log" "$OUT" <<'PY' | tee -a "$OUT/driver.log"
import re
import sys
from collections import defaultdict
from pathlib import Path

oracle_path, out_dir = map(Path, sys.argv[1:])
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
    key = (num(row.get("width")), num(row.get("origin")))
    return key if key in phases else None

def count(rows, tag, predicate=lambda row: True):
    return sum(row["tag"] == tag and predicate(row) for row in rows)

retail = {phase: {"writer_count": 0, "writer_pc": "-", "nonzero": 0} for phase in phases}
retail_nonzero = 0
if oracle_path.exists():
    with oracle_path.open(errors="replace") as stream:
        for line in stream:
            match = re.search(r"writer-pc-phase origin=0x([0-9a-f]+) width=(\d+).*pc=0x([0-9a-f]+) n=(\d+)", line)
            if match and int(match.group(2)) in (512, 1024):
                phase = (int(match.group(2)), int(match.group(1), 16))
                if phase in retail:
                    retail[phase]["writer_count"] += int(match.group(4))
                    retail[phase]["writer_pc"] = "0x" + match.group(3)
            match = re.search(r"post-value-pc watch=2 pc=0x80094648 samples=(\d+) zero=(\d+) nonzero=(\d+)", line)
            if match:
                retail_nonzero = int(match.group(3))
for phase in phases:
    retail[phase]["nonzero"] = retail_nonzero

table_header = [
    "arm", "audio", "c88", "phase", "width", "origin", "task_n", "route_ordinal",
    "route_row", "task_begin", "task_end", "task_complete", "data_ptr", "data_size",
    "output_buff", "output_buff_size", "field_writer_seq", "field_writer_pc",
    "field_writer_value", "data_ptr_plus_100_writer", "dma_count", "dma_ranges",
    "output_overlap", "pcm_source_matches", "pcm_consumer_matches", "ordering"
]
summary_header = [
    "arm", "audio", "c88", "controls", "target_tasks", "abi_rows", "output_nonzero_rows",
    "field_writer_rows", "field_writer_nonzero", "branch_rows", "fallthrough_rows",
    "dma_ranges", "overlap_ranges", "pcm_source_control", "pcm_consumer_control",
    "guest_receive", "render_rows", "keyon_rows", "filter_rows", "crash", "abort"
]
table = [table_header]
summary = [summary_header]

for arm in arms:
    rows = parse(out_dir / f"{arm}.log")
    audio = int(arm.startswith("image"))
    c88 = int(arm.endswith("_c1"))
    abi = {num(r.get("n")): r for r in rows if r["tag"] == "audtask-abi"}
    tasks = {num(r.get("n")): r for r in rows if r["tag"] == "audtask-join" and phase_key(r)}
    dma_rows = []
    current_dma_phase = None
    for row in rows:
        if row["tag"] == "audtask-dma-row":
            current_dma_phase = phase_key(row)
        elif row["tag"] == "audtask-dma-range":
            row = dict(row)
            row["_phase"] = current_dma_phase
            dma_rows.append(row)
    dma_by_n = defaultdict(list)
    for r in dma_rows:
        dma_by_n[num(r.get("n"))].append(r)
    ranges = [r for r in dma_rows if r.get("_phase") in phases]
    writers = [r for r in rows if r["tag"] == "m5-b40-writer" and phase_key(r)]
    branches = [r for r in rows if r["tag"] == "m5-synth-pregate" and phase_key(r)]
    image = [r for r in rows if r["tag"] == "audtask-image-join" and phase_key(r)]
    image_by_task = defaultdict(list)
    for r in image:
        for n, task in tasks.items():
            if num(task.get("begin")) <= num(r.get("stage_event")) <= num(task.get("end")):
                image_by_task[n].append(r)
    pcm_source = count(rows, "pcm-boundary-source")
    pcm_consumer = count(rows, "pcm-boundary-consumer")
    controls = int(
        count(rows, "vi-callers-control") > 0 and
        count(rows, "filter-voice-audit-control") > 0 and
        count(rows, "m5-audio-join-control") > 0 and
        count(rows, "audtask-abi") > 0 and
        count(rows, "audtask-dma-row") > 0 and
        count(rows, "audio-sp-route", lambda r: r.get("edge") == "guest-receive") > 0 and
        pcm_source > 0 and pcm_consumer > 0 and
        count(rows, "m5-keyon-table") > 0 and
        count(rows, "phase", lambda r: num(r.get("vi_width")) == 1024 and num(r.get("origin")) == 0x790400) > 0 and
        count(rows, "phase", lambda r: num(r.get("vi_width")) == 512 and num(r.get("origin")) == 0x6AB400) > 0
    )
    target_tasks = [(n, t) for n, t in tasks.items()]
    target_abi = [abi[n] for n, _ in target_tasks if n in abi]
    writer_by_phase = defaultdict(list)
    for writer in writers:
        writer_by_phase[(num(writer.get("width")), num(writer.get("origin")))].append(writer)
    for n, task in sorted(target_tasks):
        a = abi.get(n, {})
        phase = phase_key(task)
        task_writers = writer_by_phase[phase]
        task_image = image_by_task[n]
        task_ranges = [r for r in dma_by_n[n] if r.get("_phase") == phase]
        route = ",".join(sorted({r.get("ordinal", "-") for r in task_image})) or "-"
        route_row = ",".join(sorted({r.get("row", "-") for r in task_image})) or "-"
        field_seq = ",".join(sorted({r.get("seq", "-") for r in task_writers})) or "-"
        field_pc = ",".join(sorted({r.get("pc", "-") for r in task_writers})) or "-"
        field_value = ",".join(sorted({r.get("stored", "-") for r in task_writers})) or "-"
        retail_info = retail.get(phase, {})
        table.append([
            arm, str(audio), str(c88), "target", str(phase[0]), f"0x{phase[1]:06X}", str(n), route,
            route_row, task.get("begin", "-"), task.get("end", "-"), task.get("complete", "-"),
            a.get("data_ptr", "-"), a.get("data_size", "-"), a.get("output_buff", "-"),
            a.get("output_buff_size", "-"), field_seq, field_pc, field_value,
            f"pc={retail_info.get('writer_pc', '-')} n={retail_info.get('writer_count', 0)} nonzero={retail_info.get('nonzero', 0)}",
            str(len(task_ranges)), ",".join(r.get("dram", "-") + "/" + r.get("len", "-") for r in task_ranges) or "-",
            ",".join(sorted({r.get("output_overlap", "-") for r in task_ranges})) or "-",
            task.get("source_matches", "-"), task.get("consumer_matches", "-"),
            f"pcm_after_task={task.get('pcm_after_task', '-')} consumer_after_task={task.get('consumer_after_task', '-')}"
        ])
    output_nonzero = sum(num(a.get("output_buff")) != 0 or num(a.get("output_buff_size")) != 0 for a in target_abi)
    overlaps = sum(num(r.get("output_overlap")) != 0 for r in ranges)
    summary.append([
        arm, str(audio), str(c88), str(controls), str(len(target_tasks)), str(len(target_abi)), str(output_nonzero),
        str(len(writers)), str(sum(num(r.get("stored")) != 0 for r in writers)), str(len(branches)),
        str(sum(num(r.get("taken")) == 0 for r in branches)), str(len(ranges)), str(overlaps), str(pcm_source),
        str(pcm_consumer), str(count(rows, "audio-sp-route", lambda r: r.get("edge") == "guest-receive")),
        str(count(rows, "audtask-image-stage-row")), str(count(rows, "m5-keyon-table")),
        str(count(rows, "filter-voice-audit")), str(count(rows, "CRASH")), str(count(rows, "ABORT"))
    ])

table_path = out_dir / "phase-task-writer-table.tsv"
summary_path = out_dir / "phase-task-writer-summary.tsv"
table_path.write_text("\n".join("\t".join(row) for row in table) + "\n")
summary_path.write_text("\n".join("\t".join(row) for row in summary) + "\n")
(out_dir / "retail-output-writer.tsv").write_text(
    "width\torigin\twriter_pc\tphase_writer_count\tpost_value_nonzero_samples\n" +
    "\n".join(f"{width}\t0x{origin:06X}\t{retail[(width, origin)]['writer_pc']}\t{retail[(width, origin)]['writer_count']}\t{retail[(width, origin)]['nonzero']}" for width, origin in phases) + "\n"
)

print("output_writer_summary")
for row in summary[1:]:
    print(" ".join(f"{key}={value}" for key, value in zip(summary_header, row)))
by_arm = {row[0]: row for row in summary[1:]}
if not all(row[3] == "1" for row in summary[1:]):
    verdict = "H-CoverageInvalid"
elif not all(int(by_arm[c1][10]) > int(by_arm[c0][10]) for c0, c1 in (("stub_c0", "stub_c1"), ("image_c0", "image_c1"))):
    verdict = "H-C88TreatmentDidNotProduceQualifiedFallthrough"
elif all(int(by_arm[a][6]) == 0 for a in ("stub_c1", "image_c1")) and any(retail[p]["writer_count"] > 0 for p in phases):
    verdict = "H-RetailOutputWriterPortZero"
elif all(retail[p]["writer_count"] == 0 for p in phases) and all(int(by_arm[a][6]) == 0 for a in ("stub_c1", "image_c1")):
    verdict = "H-RetailStageOnlyLegitimate"
elif all(int(by_arm[a][12]) == 0 and int(by_arm[a][6]) > 0 for a in ("stub_c1", "image_c1")):
    verdict = "H-DmaRangeDoesNotPublish"
else:
    verdict = "H-OutputMetadataBoundaryUnresolved"
print(f"verdict={verdict}")
PY
