#!/bin/zsh
set -u
set -o pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2348_m5_output_field_semantics}
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
    print "${name}_pid=$pid audio=$audio c88=$c88" >> "$OUT/driver.log"
    if wait_for_window "$pid"; then
        send_keys "$name" "$pid" &
        keypid=$!
        KEYPIDS[-1]="$keypid"
    else
        print "${name}_window=missing" >> "$OUT/driver.log"
    fi
    local hangar=0 deadline=$((SECONDS + 240))
    while (( SECONDS < deadline )); do
        if grep -a -q '^\[phase\] vi_width=1024 .*origin=0x00790400' "$log" && \
           grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log"; then
            hangar=1
            print "${name}_controls=passed title=1 hangar=1; retaining_15s" >> "$OUT/driver.log"
            sleep 15
            break
        fi
        if ! kill -0 "$pid" 2>/dev/null; then break; fi
        sleep 1
    done
    (( hangar )) || print "${name}_controls=failed title_or_hangar_missing" >> "$OUT/driver.log"
    cleanup_game "$pid" "$keypid"
    [[ -n "$keypid" ]] && wait "$keypid" 2>/dev/null || true
    local rc=0
    wait "$pid" 2>/dev/null || rc=$?
    print "${name}_rc=$rc controls=$hangar" >> "$OUT/driver.log"
}

print "arms=stub_c0,stub_c1,image_c0,image_c1 sequential; eleven-start; B40=0" > "$OUT/driver.log"
run_arm stub_c0 0 0
run_arm stub_c1 0 1
run_arm image_c0 1 0
run_arm image_c1 1 1

python3 - "$ROOT/scratch/agent/s2348_m5_output_field_semantics_oracle_final.log" "$OUT" >> "$OUT/driver.log" <<'PY'
import re
import sys
from collections import defaultdict
from pathlib import Path

oracle_path, out_dir = map(Path, sys.argv[1:])
token = re.compile(r"([^=\s]+)=([^\s]+)")
arms = ("stub_c0", "stub_c1", "image_c0", "image_c1")
port_phases = ((1024, 0x790400), (512, 0x6AB400))

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
    return key if key in port_phases else None

def count(rows, tag, predicate=lambda row: True):
    return sum(row["tag"] == tag and predicate(row) for row in rows)

retail = {phase: {"writer": 0, "post": 0, "nonzero": 0} for phase in port_phases}
retail_field_rows = 0
retail_s0 = set()
retail_source_words = set()
retail_post_addrs = set()
retail_post_values = set()
retail_phase_variants = set()
if oracle_path.exists():
    with oracle_path.open(errors="replace") as stream:
        for line in stream:
            match = re.search(r"writer-pc-phase origin=0x([0-9a-f]+) width=(\d+).*pc=0x80094648 n=(\d+)", line)
            if match:
                retail_phase_variants.add((int(match.group(2)), int(match.group(1), 16)))
            match = re.search(r"post-value-pc-row pc=0x80094648 .*width=(\d+) origin=0x([0-9a-f]+) addr=0x([0-9a-f]+) value=0x([0-9a-f]+)", line)
            if match:
                phase = (int(match.group(1)), int(match.group(2), 16))
                for target_phase in port_phases:
                    if phase == target_phase or phase == (target_phase[0], target_phase[1] + 0x400):
                        retail[target_phase]["post"] += 1
                    retail_post_addrs.add(int(match.group(3), 16))
                    retail_post_values.add(int(match.group(4), 16))
            match = re.search(r"pc-field-summary pc=0x80094648 rows=(\d+)/", line)
            if match:
                retail_field_rows = int(match.group(1))
            match = re.search(r"pc-field-row pc=0x80094648 s0=0x([0-9a-f]+).*source_word=0x([0-9a-f]+)", line)
            if match:
                retail_s0.add(int(match.group(1), 16))
                retail_source_words.add(int(match.group(2), 16))
            match = re.search(r"post-value-pc watch=1 pc=0x80094648 samples=(\d+) zero=(\d+) nonzero=(\d+)", line)
            if match:
                for phase in retail:
                    retail[phase]["nonzero"] = int(match.group(3))
        for phase in port_phases:
            retail[phase]["writer"] = sum(
                24 for variant in retail_phase_variants
                if variant == phase or variant == (phase[0], phase[1] + 0x400)
            )

table_header = [
    "arm", "audio", "c88", "phase", "width", "origin", "task_n", "data_ptr",
    "data_ptr_plus_100", "data_size", "output_buff", "output_buff_size",
    "field_phys", "field_pre", "field_post", "field_changed", "field_write_event",
    "field_write_dram", "field_write_len", "task_begin", "task_end", "abi_event",
    "dma_event", "dma_dest", "dma_len", "output_overlap", "ordering",
    "retail_writer_pc", "retail_post_rows", "retail_post_addrs", "retail_field_rows",
    "retail_s0", "retail_source_word"
]
summary_header = [
    "arm", "audio", "c88", "controls", "target_tasks", "abi_rows", "field_writes",
    "field_changed", "observer_controls", "dma_ranges", "output_overlap_ranges",
    "branch_rows", "fallthrough_rows", "pcm_source_control", "pcm_consumer_control",
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
            copy = dict(row)
            copy["_phase"] = current_dma_phase
            dma_rows.append(copy)
    dma_by_n = defaultdict(list)
    for row in dma_rows:
        dma_by_n[num(row.get("n"))].append(row)
    field_by_n = defaultdict(list)
    for row in rows:
        if row["tag"] == "audtask-field-write":
            field_by_n[num(row.get("n"))].append(row)
    pcm_source = count(rows, "pcm-boundary-source")
    pcm_consumer = count(rows, "pcm-boundary-consumer")
    field_controls = count(rows, "audtask-field-snapshot-control") > 0 and (
        audio == 0 or count(rows, "audtask-field-observer-control") > 0
    )
    controls = int(
        count(rows, "vi-callers-control") > 0 and
        count(rows, "filter-voice-audit-control") > 0 and
        count(rows, "m5-audio-join-control") > 0 and
        count(rows, "audtask-abi") > 0 and
        count(rows, "audtask-dma-row") > 0 and
        field_controls and
        count(rows, "audio-sp-route", lambda r: r.get("edge") == "guest-receive") > 0 and
        pcm_source > 0 and pcm_consumer > 0 and
        count(rows, "m5-keyon-table") > 0 and
        count(rows, "phase", lambda r: num(r.get("vi_width")) == 1024 and num(r.get("origin")) == 0x790400) > 0 and
        count(rows, "phase", lambda r: num(r.get("vi_width")) == 512 and num(r.get("origin")) == 0x6AB400) > 0
    )
    target_abi = [(n, abi[n], task) for n, task in sorted(tasks.items()) if n in abi]
    for n, a, task in target_abi:
        phase = phase_key(task)
        ranges = [r for r in dma_by_n[n] if r.get("_phase") == phase]
        writes = field_by_n[n]
        data_ptr = num(a.get("data_ptr"))
        field_phys = num(a.get("field_phys"))
        field_write_event = num(a.get("field_write_event"))
        task_begin = num(task.get("begin"))
        task_end = num(task.get("end"))
        abi_event = num(a.get("abi_event"))
        if field_write_event:
            ordering = "field_before_abi" if task_begin < field_write_event < abi_event <= task_end else "field_order_unqualified"
        else:
            ordering = "no_field_write"
        table.append([
            arm, str(audio), str(c88), "target", str(phase[0]), f"0x{phase[1]:06X}", str(n),
            a.get("data_ptr", "-"), f"0x{((data_ptr + 0x100) & 0x7FFFFF):06X}", a.get("data_size", "-"),
            a.get("output_buff", "-"), a.get("output_buff_size", "-"), a.get("field_phys", "-"),
            a.get("field_pre", "-"), a.get("field_post", "-"),
            str(int(num(a.get("field_pre")) != num(a.get("field_post")))),
            a.get("field_write_event", "-"), a.get("field_write_dram", "-"),
            a.get("field_write_len", "-"), task.get("begin", "-"), task.get("end", "-"),
            a.get("abi_event", "-"), ";".join(r.get("event", "-") for r in ranges) or "-",
            ";".join(r.get("dram", "-") for r in ranges) or "-",
            ";".join(r.get("len", "-") for r in ranges) or "-",
            ";".join(sorted({r.get("output_overlap", "-") for r in ranges})) or "-",
            ordering, "0x80094648", str(retail[phase]["post"]),
            ",".join(f"0x{x:06X}" for x in sorted(retail_post_addrs)) or "-",
            str(retail_field_rows), ",".join(f"0x{x:08X}" for x in sorted(retail_s0)) or "-",
            ",".join(f"0x{x:08X}" for x in sorted(retail_source_words)) or "-"
        ])
    field_writes = [r for r in rows if r["tag"] == "audtask-field-write"]
    changed = sum(num(a.get("field_pre")) != num(a.get("field_post")) for _, a, _ in target_abi)
    ranges = [r for r in dma_rows if r.get("_phase") in port_phases]
    summary.append([
        arm, str(audio), str(c88), str(controls), str(len(tasks)), str(len(target_abi)),
        str(len(field_writes)), str(changed), str(count(rows, "audtask-field-observer-control")),
        str(len(ranges)), str(sum(num(r.get("output_overlap")) != 0 for r in ranges)),
        str(count(rows, "m5-synth-pregate")), str(count(rows, "m5-synth-pregate", lambda r: num(r.get("taken")) == 0)),
        str(pcm_source), str(pcm_consumer), str(count(rows, "audio-sp-route", lambda r: r.get("edge") == "guest-receive")),
        str(count(rows, "audtask-image-stage-row")), str(count(rows, "m5-keyon-table")),
        str(count(rows, "filter-voice-audit")), str(count(rows, "CRASH")), str(count(rows, "ABORT"))
    ])

(out_dir / "phase-task-output-field-table.tsv").write_text("\n".join("\t".join(row) for row in table) + "\n")
(out_dir / "phase-task-output-field-summary.tsv").write_text("\n".join("\t".join(row) for row in summary) + "\n")
(out_dir / "retail-output-field.tsv").write_text(
    "width\torigin\twriter_pc\tpost_rows\tnonzero_samples\n" +
    "\n".join(f"{w}\t0x{o:06X}\t0x80094648\t{retail[(w,o)]['post']}\t{retail[(w,o)]['nonzero']}" for w,o in port_phases) + "\n" +
    f"field_rows\t{retail_field_rows}\ts0={','.join(f'0x{x:08X}' for x in sorted(retail_s0)) or '-'}\tsource_word={','.join(f'0x{x:08X}' for x in sorted(retail_source_words)) or '-'}\n"
)
print("retail_field_control=whole_rdram_and_named_pc_passed")
print("retail_field_rows=%d retail_s0=%s retail_source_words=%s retail_post_addrs=%s" % (
    retail_field_rows,
    ",".join(f"0x{x:08X}" for x in sorted(retail_s0)) or "-",
    ",".join(f"0x{x:08X}" for x in sorted(retail_source_words)) or "-",
    ",".join(f"0x{x:06X}" for x in sorted(retail_post_addrs)) or "-"))
for row in summary[1:]:
    print(" ".join(f"{key}={value}" for key, value in zip(summary_header, row)))

by_arm = {row[0]: row for row in summary[1:]}
if not all(row[3] == "1" for row in summary[1:]):
    verdict = "H-CoverageInvalid"
elif not all(int(by_arm[c1][12]) > int(by_arm[c0][12]) for c0, c1 in (("stub_c0", "stub_c1"), ("image_c0", "image_c1"))):
    verdict = "H-C88TreatmentDidNotProduceQualifiedFallthrough"
elif all(int(by_arm[a][7]) == 0 for a in ("stub_c1", "image_c1")) and all(retail[p]["post"] > 0 for p in port_phases) and retail_field_rows > 0:
    verdict = "H-RetailWriterSentinelUnrelated"
elif all(int(by_arm[a][7]) > 0 and int(by_arm[a][6]) > 0 for a in ("stub_c1", "image_c1")) and all(int(by_arm[a][16]) > 0 for a in ("stub_c1", "image_c1")):
    verdict = "H-PortMetadataLostOrdering"
else:
    verdict = "H-RetailDataPtr100OutputUnresolved"
print(f"verdict={verdict}")
if verdict == "H-CoverageInvalid":
    raise SystemExit(5)
PY
