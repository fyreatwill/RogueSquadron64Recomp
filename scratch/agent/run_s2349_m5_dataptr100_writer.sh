#!/bin/zsh
set -u
set -o pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2349_m5_dataptr100_writer}
OUT="$ROOT/scratch/agent/$TAG"
ORACLE="$ROOT/scratch/agent/s2349_m5_dataptr100_writer_oracle.log"
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
    local reached=0 deadline=$((SECONDS + 240))
    while (( SECONDS < deadline )); do
        if grep -a -q '^\[phase\] vi_width=1024 .*origin=0x00790400' "$log" && \
           grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log"; then
            reached=1
            print "${name}_controls=passed title=1 hangar=1; retaining_15s" >> "$OUT/driver.log"
            sleep 15
            break
        fi
        if ! kill -0 "$pid" 2>/dev/null; then break; fi
        sleep 1
    done
    (( reached )) || print "${name}_controls=failed title_or_hangar_missing" >> "$OUT/driver.log"
    cleanup_game "$pid" "$keypid"
    [[ -n "$keypid" ]] && wait "$keypid" 2>/dev/null || true
    local rc=0
    wait "$pid" 2>/dev/null || rc=$?
    print "${name}_rc=$rc controls=$reached" >> "$OUT/driver.log"
}

if [[ "${ROGUESQ_PARSE_ONLY:-0}" != 1 ]]; then
    print "arms=stub_c0,stub_c1,image_c0,image_c1 sequential; eleven-start; B40=0" > "$OUT/driver.log"
    run_arm stub_c0 0 0
    run_arm stub_c1 0 1
    run_arm image_c0 1 0
    run_arm image_c1 1 1
fi

python3 - "$ORACLE" "$OUT" <<'PY'
import re
import sys
from collections import defaultdict
from pathlib import Path

oracle_path, out_dir = map(Path, sys.argv[1:])
token = re.compile(r"([A-Za-z0-9_]+)=([^\s]+)")
arms = ("stub_c0", "stub_c1", "image_c0", "image_c1")
phases = ((1024, 0x790400), (512, 0x6AB400))

def num(value):
    try:
        return int(value, 0)
    except (TypeError, ValueError):
        return 0

def parse(path):
    rows = []
    if not path.exists():
        return rows
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

def canonical_phase(width, origin):
    key = (width, origin)
    for phase in phases:
        if key == phase or key == (phase[0], phase[1] + 0x400):
            return phase
    return None

def count(rows, tag, predicate=lambda row: True):
    return sum(row["tag"] == tag and predicate(row) for row in rows)

retail_writer_phase = defaultdict(int)
retail_post = defaultdict(list)
retail_watch_hits = {}
retail_phase_hist = set()
retail_named_pc = 0
retail_whole = 0
retail_target_window = 0
if oracle_path.exists():
    with oracle_path.open(errors="replace") as stream:
        for line in stream:
            match = re.search(r"watch write \[0x([0-9a-f]+),0x([0-9a-f]+)\): (\d+) hit", line, re.I)
            if match:
                start = int(match.group(1), 16)
                hits = int(match.group(3))
                retail_watch_hits[start] = hits
                if start == 0:
                    retail_whole = hits
                if start == 0x149470:
                    retail_target_window = hits
            match = re.search(r"pc-hist-phase origin=0x([0-9a-f]+) width=(\d+)", line, re.I)
            if match:
                phase = canonical_phase(int(match.group(2)), int(match.group(1), 16))
                if phase:
                    retail_phase_hist.add(phase)
            match = re.search(r"writer-pc-phase origin=0x([0-9a-f]+) width=(\d+).*watch=([23]) .*pc=0x80090ca4 n=(\d+)", line, re.I)
            if match:
                phase = canonical_phase(int(match.group(2)), int(match.group(1), 16))
                if phase:
                    retail_writer_phase[phase] += int(match.group(4))
            match = re.search(r"post-value-pc-row pc=0x80090ca4 .*width=(\d+) origin=0x([0-9a-f]+) addr=0x([0-9a-f]+) value=0x([0-9a-f]+)", line, re.I)
            if match:
                phase = canonical_phase(int(match.group(1)), int(match.group(2), 16))
                if phase:
                    retail_post[(phase, int(match.group(3), 16))].append(int(match.group(4), 16))
            match = re.search(r"watch pc \[0x800078ec,.*\): (\d+) hit", line, re.I)
            if match:
                retail_named_pc = int(match.group(1))

table_header = [
    "arm", "audio", "c88", "phase", "width", "origin", "retail_writer_pc",
    "retail_task_ptr", "retail_dest", "retail_post_rows", "retail_nonzero",
    "task_n", "data_ptr", "data_ptr_plus_100", "field_phys", "field_pre",
    "field_post", "field_changed", "field_write_event", "field_write_dram",
    "field_write_len", "task_begin", "task_end", "abi_event", "dma_event",
    "dma_dest", "dma_len", "ordering"
]
summary_header = [
    "arm", "audio", "c88", "controls", "title", "hangar", "target_tasks",
    "abi_rows", "field_write_events", "field_changed", "dma_ranges",
    "field_observer_controls", "pcm_source", "pcm_consumer", "guest_receive",
    "render_rows", "keyon_rows", "filter_rows", "retail_exact_rows",
    "retail_nonzero", "crash", "abort"
]
table = [table_header]
summary = [summary_header]

for arm in arms:
    rows = parse(out_dir / f"{arm}.log")
    audio = int(arm.startswith("image"))
    c88 = int(arm.endswith("_c1"))
    abi = {num(row.get("n")): row for row in rows if row["tag"] == "audtask-abi"}
    tasks = {num(row.get("n")): row for row in rows if row["tag"] == "audtask-join" and phase_key(row)}
    dma_by_n = defaultdict(list)
    current_n = None
    for row in rows:
        if row["tag"] == "audtask-dma-row":
            current_n = num(row.get("n"))
        elif row["tag"] == "audtask-dma-range" and current_n is not None:
            dma_by_n[current_n].append(row)
    field_writes = defaultdict(list)
    for row in rows:
        if row["tag"] == "audtask-field-write":
            field_writes[num(row.get("n"))].append(row)
    title = count(rows, "phase", lambda r: num(r.get("vi_width")) == 1024 and num(r.get("origin")) == 0x790400)
    hangar = count(rows, "phase", lambda r: num(r.get("vi_width")) == 512 and num(r.get("origin")) == 0x6AB400)
    field_snapshot = count(rows, "audtask-field-snapshot-control")
    field_observer = count(rows, "audtask-field-observer-control")
    source = count(rows, "pcm-boundary-source")
    consumer = count(rows, "pcm-boundary-consumer")
    controls = int(
        title > 0 and hangar > 0 and
        count(rows, "vi-callers-control") > 0 and
        count(rows, "filter-voice-audit-control") > 0 and
        count(rows, "m5-audio-join-control") > 0 and
        count(rows, "audtask-abi") > 0 and
        count(rows, "audtask-dma-row") > 0 and
        field_snapshot > 0 and (not audio or field_observer > 0) and
        count(rows, "audio-sp-route", lambda r: r.get("edge") == "guest-receive") > 0 and
        source > 0 and consumer > 0 and count(rows, "m5-keyon-table") > 0
    )
    target = [(n, abi[n], task) for n, task in sorted(tasks.items()) if n in abi]
    for n, abi_row, task in target:
        phase = phase_key(task)
        data_ptr = num(abi_row.get("data_ptr"))
        field = num(abi_row.get("field_phys"))
        field_dest = field
        post_values = retail_post.get((phase, field_dest), [])
        retail_ptr = (0x80000000 | ((field_dest - 0x100) & 0x7FFFFF)) if field_dest else 0
        writes = field_writes[n]
        field_event = num(abi_row.get("field_write_event"))
        begin = num(task.get("begin"))
        end = num(task.get("end"))
        abi_event = num(abi_row.get("abi_event"))
        if field_event and begin < field_event < abi_event <= end:
            ordering = "field_before_abi"
        elif field_event:
            ordering = "field_order_unqualified"
        else:
            ordering = "no_field_write"
        table.append([
            arm, str(audio), str(c88), "target", str(phase[0]), f"0x{phase[1]:06X}",
            "0x80090CA4", f"0x{retail_ptr:08X}" if retail_ptr else "-",
            f"0x{field_dest:06X}" if field_dest else "-", str(len(post_values)),
            str(sum(value != 0 for value in post_values)), str(n),
            abi_row.get("data_ptr", "-"), f"0x{((data_ptr + 0x100) & 0x7FFFFF):06X}" if data_ptr else "-",
            abi_row.get("field_phys", "-"), abi_row.get("field_pre", "-"),
            abi_row.get("field_post", "-"), str(int(num(abi_row.get("field_pre")) != num(abi_row.get("field_post")))),
            abi_row.get("field_write_event", "-"), abi_row.get("field_write_dram", "-"),
            abi_row.get("field_write_len", "-"), task.get("begin", "-"), task.get("end", "-"),
            abi_row.get("abi_event", "-"), ";".join(r.get("event", "-") for r in dma_by_n[n]) or "-",
            ";".join(r.get("dram", "-") for r in dma_by_n[n]) or "-",
            ";".join(r.get("len", "-") for r in dma_by_n[n]) or "-", ordering
        ])
    changed = sum(num(a.get("field_pre")) != num(a.get("field_post")) for _, a, _ in target)
    target_pairs = [(phase_key(task), num(a.get("field_phys"))) for _, a, task in target]
    retail_rows = sum(len(retail_post.get((phase, field), [])) for phase, field in target_pairs)
    retail_nz = sum(sum(value != 0 for value in retail_post.get((phase, field), [])) for phase, field in target_pairs)
    summary.append([
        arm, str(audio), str(c88), str(controls), str(title), str(hangar), str(len(tasks)), str(len(target)),
        str(sum(len(v) for v in field_writes.values())), str(changed),
        str(sum(len(v) for v in dma_by_n.values())), str(field_observer), str(source), str(consumer),
        str(count(rows, "audio-sp-route", lambda r: r.get("edge") == "guest-receive")),
        str(count(rows, "audtask-image-stage-row")), str(count(rows, "m5-keyon-table")),
        str(count(rows, "filter-voice-audit")), str(retail_rows), str(retail_nz),
        str(count(rows, "CRASH")), str(count(rows, "ABORT"))
    ])

(out_dir / "phase-task-dataptr100-table.tsv").write_text("\n".join("\t".join(row) for row in table) + "\n")
(out_dir / "phase-task-dataptr100-summary.tsv").write_text("\n".join("\t".join(row) for row in summary) + "\n")
(out_dir / "retail-dataptr100-summary.tsv").write_text(
    "phase\twriter_pc_phase\tphase_hist\twatch_task_hits\twatch_field_hits\tpost_rows_173c20\tpost_rows_171de0\tnamed_pc\twhole_rdram\ttarget_window\n" +
    "\n".join(
        f"{w}:{o:06X}\t{retail_writer_phase[(w,o)]}\t{int((w,o) in retail_phase_hist)}\t{retail_watch_hits.get(0x173C20, 0)}\t{retail_watch_hits.get(0x171DE0, 0)}\t{len(retail_post.get(((w,o), 0x173C20), []))}\t{len(retail_post.get(((w,o), 0x171DE0), []))}\t{retail_named_pc}\t{retail_whole}\t{retail_target_window}"
        for w, o in phases
    ) + "\n"
)

by_arm = {row[0]: row for row in summary[1:]}
retail_positive = all(retail_writer_phase[p] > 0 and p in retail_phase_hist for p in phases)
exact_dest_positive = all(
    retail_watch_hits.get(field, 0) > 0 and
    any(retail_post.get((phase, field), []) for phase in phases)
    for field in (0x173C20, 0x171DE0)
)
print(f"retail_controls whole_rdram={retail_whole} target_window={retail_target_window} named_pc={retail_named_pc} writer_phase={dict(retail_writer_phase)} exact_dest={int(exact_dest_positive)}")
for row in summary[1:]:
    print(" ".join(f"{key}={value}" for key, value in zip(summary_header, row)))
if not all(row[3] == "1" for row in summary[1:]) or not retail_whole or not retail_target_window:
    verdict = "H-CoverageInvalid"
elif not retail_positive or not exact_dest_positive:
    verdict = "H-RetailKnownDestNotAudioOutput"
elif all(int(by_arm[a][9]) == 0 for a in ("stub_c1", "image_c1")) and all(
    int(by_arm[a][8]) == 0 for a in ("stub_c1", "image_c1")
):
    verdict = "H-RetailDataPtr100PortAbsent"
elif all(int(by_arm[a][9]) > 0 and int(by_arm[a][8]) > 0 for a in ("stub_c1", "image_c1")):
    verdict = "H-PortDataPtr100WriterPresent"
else:
    verdict = "H-RetailDataPtr100OutputUnresolved"
print(f"verdict={verdict}")
if verdict == "H-CoverageInvalid":
    raise SystemExit(5)
PY
