#!/bin/zsh
set -u
set -o pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2350_m5_hangar_writer}
OUT="$ROOT/scratch/agent/$TAG"
ORACLE="${RS64_ORACLE:-$ROOT/scratch/agent/s2350_m5_hangar_writer_oracle.log}"
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
known_candidates = (0x800908D4, 0x8009081C, 0x80090810)
named_controls = (
    0x800078EC, 0x800908D4, 0x8009081C, 0x80090810, 0x80090CA4,
    0x80094648, 0x8008EC88, 0x80091468, 0x800914A4, 0x80091564,
    0x80091618, 0x8008C9AC, 0x8008CA14, 0x80019B74, 0x8009B5A8,
    0x80092128, 0x80092230, 0x8009231C, 0x80090B68, 0x80090C28,
    0x8009C904, 0x8009D740, 0x8009D7D0,
)

def num(value):
    try:
        return int(value, 0)
    except (TypeError, ValueError):
        return 0

def canonical(width, origin):
    for phase in phases:
        if (width, origin) == phase or (width, origin) == (phase[0], phase[1] + 0x400):
            return phase
    return None

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

def count(rows, tag, predicate=lambda row: True):
    return sum(row["tag"] == tag and predicate(row) for row in rows)

retail_watch = {}
retail_phase_hist = set()
retail_phase_origins = set()
retail_phase_writer = defaultdict(int)
retail_phase_pc = defaultdict(lambda: defaultdict(int))
retail_named = {}
if oracle_path.exists():
    text = oracle_path.read_text(errors="replace")
    for match in re.finditer(r"watch write \[0x([0-9a-f]+),0x[0-9a-f]+\): (\d+) hit", text, re.I):
        retail_watch[int(match.group(1), 16)] = int(match.group(2))
    for match in re.finditer(r"pc-hist-phase origin=0x([0-9a-f]+) width=(\d+)", text, re.I):
        width = int(match.group(2))
        origin = int(match.group(1), 16)
        retail_phase_origins.add((width, origin))
        phase = canonical(width, origin)
        if phase:
            retail_phase_hist.add(phase)
    for match in re.finditer(
            r"writer-pc-phase origin=0x([0-9a-f]+) width=(\d+) watch=(\d+) .*pc=0x([0-9a-f]+) n=(\d+)",
            text, re.I):
        phase = canonical(int(match.group(2)), int(match.group(1), 16))
        if not phase:
            continue
        watch = int(match.group(3))
        pc = int(match.group(4), 16)
        n = int(match.group(5))
        retail_phase_writer[(phase, watch)] += n
        retail_phase_pc[(phase, watch)][pc] += n
    for match in re.finditer(r"watch pc \[0x([0-9a-f]+),0x[0-9a-f]+\): (\d+) hit", text, re.I):
        retail_named[int(match.group(1), 16)] = int(match.group(2))

retail_controls = (
    retail_watch.get(0, 0) > 0 and
    retail_watch.get(0x149470, 0) > 0 and
    retail_watch.get(0x173C20, 0) > 0 and
    retail_watch.get(0x171DE0, 0) > 0 and
    all(phase in retail_phase_hist for phase in phases) and
    all(origin in retail_phase_origins for origin in ((512, 0x6AB400), (512, 0x6AB800))) and
    all(retail_named.get(pc, 0) > 0 for pc in named_controls)
)
candidate_phase_controls = all(
    all(retail_phase_pc[(phase, 3)].get(pc, 0) > 0 for pc in known_candidates)
    for phase in phases if phase[0] == 512
)
retail_field2_pcs = {phase: retail_phase_pc[(phase, 2)] for phase in phases}
retail_field2_hangar_rows = sum(retail_field2_pcs[(512, 0x6AB400)].values())
retail_field2_hangar_pcs = ",".join(
    f"0x{pc:08X}:{n}" for pc, n in sorted(retail_field2_pcs[(512, 0x6AB400)].items())
)

table_header = [
    "arm", "audio", "c88", "controls", "phase", "width", "origin", "task_n",
    "data_ptr", "data_ptr_plus_100", "field_phys", "field_pre", "field_post",
    "field_changed", "field_write_event", "field_write_dram", "field_write_len",
    "task_begin", "task_end", "abi_event", "dma_event", "ordering",
    "retail_field2_writer_pcs"
]
summary_header = [
    "arm", "audio", "c88", "controls", "title", "hangar", "target_tasks", "abi_rows",
    "field_write_events", "field_changed", "ordered_field_rows", "dma_ranges", "field_snapshot_controls",
    "field_observer_controls", "pcm_source", "pcm_consumer", "guest_receive",
    "render_rows", "keyon_rows", "filter_rows", "crash", "abort"
]
table = [table_header]
summary = [summary_header]

for arm in arms:
    rows = parse(out_dir / f"{arm}.log")
    audio = int(arm.startswith("image"))
    c88 = int(arm.endswith("_c1"))
    abi = {num(row.get("n")): row for row in rows if row["tag"] == "audtask-abi"}
    joins = {num(row.get("n")): row for row in rows if row["tag"] == "audtask-join"}
    field_writes = defaultdict(list)
    for row in rows:
        if row["tag"] == "audtask-field-write":
            field_writes[num(row.get("n"))].append(row)
    title = count(rows, "phase", lambda r: num(r.get("vi_width")) == 1024 and num(r.get("origin")) == 0x790400)
    hangar = count(rows, "phase", lambda r: num(r.get("vi_width")) == 512 and num(r.get("origin")) == 0x6AB400)
    snapshot = count(rows, "audtask-field-snapshot-control")
    observer = count(rows, "audtask-field-observer-control")
    source = count(rows, "pcm-boundary-source")
    consumer = count(rows, "pcm-boundary-consumer")
    guest = count(rows, "audio-sp-route", lambda r: r.get("edge") == "guest-receive")
    controls = int(
        title > 0 and hangar > 0 and
        count(rows, "vi-callers-control") > 0 and
        count(rows, "filter-voice-audit-control") > 0 and
        count(rows, "m5-audio-join-control") > 0 and
        len(abi) > 0 and count(rows, "audtask-dma-row") > 0 and
        snapshot > 0 and (not audio or observer > 0) and
        guest > 0 and source > 0 and consumer > 0 and count(rows, "m5-keyon-table") > 0
    )
    target = []
    for n, abi_row in sorted(abi.items()):
        join = joins.get(n)
        if not join:
            continue
        phase = canonical(num(join.get("width")), num(join.get("origin")))
        if phase:
            target.append((n, abi_row, join, phase))
    for n, abi_row, join, phase in target:
        field_event = num(abi_row.get("field_write_event"))
        begin = num(join.get("begin"))
        end = num(join.get("end"))
        abi_event = num(abi_row.get("abi_event"))
        if field_event and begin < field_event < abi_event <= end:
            ordering = "field_before_abi"
        elif field_event:
            ordering = "field_order_unqualified"
        else:
            ordering = "no_field_write"
        changed = int(num(abi_row.get("field_pre")) != num(abi_row.get("field_post")))
        table.append([
            arm, str(audio), str(c88), str(controls), "target", str(phase[0]),
            f"0x{phase[1]:06X}", str(n), abi_row.get("data_ptr", "-"),
            f"0x{((num(abi_row.get('data_ptr')) + 0x100) & 0x7FFFFF):06X}",
            abi_row.get("field_phys", "-"), abi_row.get("field_pre", "-"),
            abi_row.get("field_post", "-"), str(changed),
            abi_row.get("field_write_event", "-"), abi_row.get("field_write_dram", "-"),
            abi_row.get("field_write_len", "-"), join.get("begin", "-"),
            join.get("end", "-"), abi_row.get("abi_event", "-"),
            str(len([r for r in rows if r["tag"] == "audtask-dma-range" and num(r.get("n")) == n])),
            ordering,
            ",".join(f"0x{pc:08X}:{count}" for pc, count in sorted(retail_field2_pcs[phase].items())) or "-"
        ])
    changed = sum(num(row.get("field_pre")) != num(row.get("field_post")) for _, row, _, _ in target)
    field_events = sum(len(v) for v in field_writes.values())
    ordered_field_rows = sum(
        1 for _, abi_row, join, _ in target
        if num(abi_row.get("field_write_event")) and
        num(join.get("begin")) < num(abi_row.get("field_write_event")) < num(abi_row.get("abi_event")) <= num(join.get("end"))
    )
    dma_ranges = count(rows, "audtask-dma-range")
    summary.append([
        arm, str(audio), str(c88), str(controls), str(title), str(hangar),
        str(len(target)), str(len(abi)), str(field_events), str(changed), str(ordered_field_rows), str(dma_ranges),
        str(snapshot), str(observer), str(source), str(consumer), str(guest),
        str(count(rows, "audtask-image-stage-row")), str(count(rows, "m5-keyon-table")),
        str(count(rows, "filter-voice-audit")), str(count(rows, "CRASH")), str(count(rows, "ABORT"))
    ])

(out_dir / "phase-task-hangar-writer-table.tsv").write_text(
    "\n".join("\t".join(row) for row in table) + "\n"
)
(out_dir / "phase-task-hangar-writer-summary.tsv").write_text(
    "\n".join("\t".join(row) for row in summary) + "\n"
)
(out_dir / "retail-hangar-writer-summary.tsv").write_text(
    "phase\tphase_hist\tphase_origins\tfield2_writer_rows\tfield2_writer_pcs\tfield3_candidate_rows\tcandidate_pcs\twhole_rdram\ttarget_window\n" +
    "\n".join(
        f"{w}:{o:06X}\t{int((w, o) in retail_phase_hist)}\t"
        f"{','.join(f'0x{origin:06X}' for width, origin in sorted(retail_phase_origins) if canonical(width, origin) == (w, o)) or '-'}\t"
        f"{sum(retail_field2_pcs[(w, o)].values())}\t"
        f"{','.join(f'0x{pc:08X}:{n}' for pc, n in sorted(retail_field2_pcs[(w, o)].items())) or '-'}\t"
        f"{sum(retail_phase_pc[((w, o), 3)].get(pc, 0) for pc in known_candidates)}\t"
        f"{sum(retail_named.get(pc, 0) > 0 for pc in known_candidates)}/{len(known_candidates)}\t"
        f"{retail_watch.get(0, 0)}\t{retail_watch.get(0x149470, 0)}"
        for w, o in phases
    ) + "\n"
)

by_arm = {row[0]: row for row in summary[1:]}
port_controls = all(row[3] == "1" for row in summary[1:])
port_treatment_changed = all(
    int(by_arm[arm][9]) > 0 and int(by_arm[arm][8]) > 0 and int(by_arm[arm][10]) > 0
    for arm in ("stub_c1", "image_c1")
)
retail_matches = retail_field2_hangar_rows > 0
if not retail_controls or not candidate_phase_controls or not port_controls:
    verdict = "H-CoverageInvalid"
elif port_treatment_changed:
    verdict = "H-PortHangarFieldWriterPresent"
elif retail_matches:
    verdict = "H-RetailHangarFieldWriterPresent"
else:
    verdict = "H-RetailHangarFieldUnwritten"

print(
    f"retail_controls={int(retail_controls)} whole_rdram={retail_watch.get(0, 0)} "
    f"target_window={retail_watch.get(0x149470, 0)} named_controls="
    f"{sum(retail_named.get(pc, 0) > 0 for pc in named_controls)}/{len(named_controls)} "
    f"candidate_phase_controls={int(candidate_phase_controls)} "
    f"hangar_origin_controls={int(all(origin in retail_phase_origins for origin in ((512, 0x6AB400), (512, 0x6AB800))))}"
)
print(
    f"hangar_field2_writer_rows={retail_field2_hangar_rows} "
    f"hangar_field2_writer_pcs={retail_field2_hangar_pcs or '-'} "
    f"hangar_field3_candidate_rows={sum(retail_phase_pc[((512, 0x6AB400), 3)].get(pc, 0) for pc in known_candidates)} "
    f"retail_matches={int(retail_matches)} "
    f"port_controls={int(port_controls)} port_treatment_changed={int(port_treatment_changed)}"
)
for row in summary[1:]:
    print(" ".join(f"{key}={value}" for key, value in zip(summary_header, row)))
print(f"verdict={verdict}")
if verdict == "H-CoverageInvalid":
    raise SystemExit(5)
PY
