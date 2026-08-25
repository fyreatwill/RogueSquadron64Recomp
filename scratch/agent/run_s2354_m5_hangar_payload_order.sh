#!/bin/zsh
set -u
set -o pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TAG=${1:-s2354_m5_hangar_payload_order}
OUT="$ROOT/scratch/agent/$TAG"
ORACLE="${RS64_ORACLE:-$ROOT/scratch/agent/s2354_m5_hangar_payload_order_oracle.log}"
PORT="$ROOT/scratch/agent/s2352_m5_writer_placement"

[[ "$TAG" != .* ]] || exit 2
[[ -f "$ORACLE" && -f "$PORT/phase-task-writer-placement-table.tsv" && -f "$PORT/phase-task-writer-placement-summary.tsv" ]] || exit 3
mkdir -p "$OUT"

python3 - "$ORACLE" "$PORT" "$OUT" <<'PY'
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

oracle_path, port_dir, out_dir = map(Path, sys.argv[1:])
phases = ((1024, 0x790400), (1024, 0x790800), (512, 0x6AB400), (512, 0x6AB800))
hangar_phases = {(512, 0x6AB400), (512, 0x6AB800)}
watch_fields = {2: 0x173C20, 3: 0x171DE0, 4: 0x171F70, 5: 0x173DB0}
named_controls = (
    0x800078EC, 0x800908D4, 0x8009081C, 0x80090810, 0x80090CA4,
    0x80094648, 0x8008EC88, 0x80091468, 0x800914A4, 0x80091564,
    0x80091618, 0x8008C9AC, 0x8008CA14, 0x80019B74, 0x8009B5A8,
    0x80092128, 0x80092230, 0x8009231C, 0x80090B68, 0x80090C28,
    0x8009C904, 0x8009D740, 0x8009D7D0,
)

def number(value):
    try:
        return int(value, 0)
    except (TypeError, ValueError):
        return 0

def read_tsv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))

text = oracle_path.read_text(errors="replace")
watch_hits = {}
for match in re.finditer(r"watch write \[0x([0-9a-f]+),0x[0-9a-f]+\): (\d+) hit", text, re.I):
    watch_hits[int(match.group(1), 16)] = int(match.group(2))

named_hits = {}
for match in re.finditer(r"watch pc \[0x([0-9a-f]+),0x[0-9a-f]+\): (\d+) hit", text, re.I):
    named_hits[int(match.group(1), 16)] = int(match.group(2))

phase_hist = set()
for match in re.finditer(r"pc-hist-phase origin=0x([0-9a-f]+) width=(\d+)", text, re.I):
    phase = (int(match.group(2)), int(match.group(1), 16))
    if phase in phases:
        phase_hist.add(phase)

writer_pcs = defaultdict(lambda: defaultdict(int))
for match in re.finditer(
        r"writer-pc-phase origin=0x([0-9a-f]+) width=(\d+) watch=(\d+) .*?pc=0x([0-9a-f]+) n=(\d+)",
        text, re.I):
    phase = (int(match.group(2)), int(match.group(1), 16))
    watch = int(match.group(3))
    if phase in phases and watch in watch_fields:
        writer_pcs[(phase, watch)][int(match.group(4), 16)] += int(match.group(5))

detail_rows = defaultdict(list)
for match in re.finditer(
        r"post-value-pc-row pc=0x([0-9a-f]+) vi=(\d+) width=(\d+) origin=0x([0-9a-f]+) addr=0x([0-9a-f]+) value=0x([0-9a-f]+)",
        text, re.I):
    pc = int(match.group(1), 16)
    phase = (int(match.group(3)), int(match.group(4), 16))
    addr = int(match.group(5), 16)
    if phase in phases and addr in watch_fields.values():
        detail_rows[(phase, pc, addr)].append((int(match.group(2)), int(match.group(6), 16)))

overflow_match = re.search(r"post-value-pc-detail-overflow n=(\d+)", text, re.I)
detail_overflow = number(overflow_match.group(1)) if overflow_match else 0

port_rows = read_tsv(port_dir / "phase-task-writer-placement-table.tsv")
port_summary = read_tsv(port_dir / "phase-task-writer-placement-summary.tsv")
port_hangar_fields = {
    number(row.get("field_phys"))
    for row in port_rows
    if number(row.get("width")) == 512 and number(row.get("origin")) in {0x6AB400, 0x6AB800}
}
expected_hangar_fields = {watch_fields[3], watch_fields[4], watch_fields[5]}
port_controls = (
    len(port_summary) == 4 and
    all(row.get("controls") == "1" and row.get("title", "0") != "0" and row.get("hangar", "0") != "0" for row in port_summary) and
    expected_hangar_fields <= port_hangar_fields
)

def port_matches(phase, field):
    return [
        row for row in port_rows
        if number(row.get("width")) == phase[0] and number(row.get("origin")) == phase[1] and number(row.get("field_phys")) == field
    ]

def joined_values(rows, key):
    values = sorted({row.get(key, "-") or "-" for row in rows})
    return ",".join(values) or "-"

header = [
    "phase", "width", "origin", "writer_pc", "field_phys", "writer_rows",
    "detail_rows", "detail_nonzero", "detail_vis", "detail_values",
    "detail_overflow", "port_arms", "port_rows", "field_pre", "field_post",
    "task_intervals", "abi_events", "ordering", "payload_join",
]
table = [header]
positive_hangar_keys = []
positive_hangar_detail = []
payload_matches = []
for phase in phases:
    for watch, field in watch_fields.items():
        pcs = writer_pcs[(phase, watch)]
        items = sorted(pcs.items()) or [(0, 0)]
        for pc, rows in items:
            details = detail_rows[(phase, pc, field)]
            ports = port_matches(phase, field)
            if phase in hangar_phases and watch in (3, 4, 5) and rows > 0:
                key = (phase, pc, field)
                positive_hangar_keys.append(key)
                if details:
                    positive_hangar_detail.append(key)
            detail_values = {value for _, value in details}
            port_values = {number(row.get("field_pre")) for row in ports} | {number(row.get("field_post")) for row in ports}
            if details and ports and detail_values & port_values:
                payload_matches.append((phase, pc, field))
            payload_join = (
                "value_intersection" if details and ports and detail_values & port_values else
                "detail_without_port_row" if details and not ports else
                "port_without_detail" if ports and not details else
                "unjoined"
            )
            table.append([
                f"{phase[0]}:0x{phase[1]:06X}", str(phase[0]), f"0x{phase[1]:06X}",
                f"0x{pc:08X}" if pc else "-", f"0x{field:06X}", str(rows),
                str(len(details)), str(sum(value != 0 for _, value in details)),
                ",".join(str(vi) for vi, _ in details) or "-",
                ",".join(f"0x{value:08X}" for value in sorted(detail_values)) or "-",
                str(detail_overflow),
                ",".join(sorted({row.get("arm", "-") for row in ports})) or "-",
                str(len(ports)), joined_values(ports, "field_pre"), joined_values(ports, "field_post"),
                ",".join(f"{row.get('task_begin', '-')}-{row.get('task_end', '-')}" for row in ports[:8]) or "-",
                ",".join(row.get("abi_event", "-") or "-" for row in ports[:8]) or "-",
                joined_values(ports, "ordering"), payload_join,
            ])

(out_dir / "retail-hangar-payload-order-table.tsv").write_text(
    "\n".join("\t".join(row) for row in table) + "\n"
)

whole = watch_hits.get(0, 0) > 0
target = watch_hits.get(0x149470, 0) > 0
exact = all(watch_hits.get(field, 0) > 0 for field in watch_fields.values())
named_ok = all(named_hits.get(pc, 0) > 0 for pc in named_controls)
phase_ok = phase_hist == set(phases)
hangar_writers_ok = bool(positive_hangar_keys)
hangar_detail_complete = bool(positive_hangar_keys) and all(detail_rows[key] for key in positive_hangar_keys)

summary = [
    f"retail_controls={int(whole and target and exact and phase_ok and named_ok)}",
    f"whole_rdram={watch_hits.get(0, 0)}",
    f"target_window={watch_hits.get(0x149470, 0)}",
    f"exact_fields={','.join(str(watch_hits.get(field, 0)) for field in watch_fields.values())}",
    f"phase_controls={int(phase_ok)}",
    f"named_controls={sum(named_hits.get(pc, 0) > 0 for pc in named_controls)}/{len(named_controls)}",
    f"port_controls={int(port_controls)}",
    f"port_hangar_fields={','.join(f'0x{x:06X}' for x in sorted(port_hangar_fields)) or '-'}",
    f"hangar_writer_keys={len(positive_hangar_keys)}",
    f"hangar_detail_keys={len(positive_hangar_detail)}",
    f"detail_overflow={detail_overflow}",
    f"detail_rows={sum(len(rows) for rows in detail_rows.values())}",
]
print(" ".join(summary))
for phase in phases:
    print(
        f"phase={phase[0]}:{phase[1]:06X} hist={int(phase in phase_hist)} " +
        " ".join(
            f"watch{watch}=" + (",".join(f"0x{pc:08X}:{rows}" for pc, rows in sorted(writer_pcs[(phase, watch)].items())) or "-")
            for watch in (2, 3, 4, 5)
        )
    )

if not (whole and target and exact and phase_ok and named_ok and port_controls):
    verdict = "H-CoverageInvalid"
elif hangar_writers_ok and not hangar_detail_complete and detail_overflow:
    verdict = "H-RetailWriterOrderUnresolved"
elif hangar_detail_complete and len(payload_matches) == len(positive_hangar_keys):
    verdict = "H-RetailPayloadMatchesPortField"
elif hangar_detail_complete:
    verdict = "H-RetailWriterIsUnrelated"
else:
    verdict = "H-RetailWriterOrderUnresolved"
print(f"hangar_detail_complete={int(hangar_detail_complete)} payload_matches={len(payload_matches)} verdict={verdict}")
(out_dir / "summary.txt").write_text(" ".join(summary) + f" verdict={verdict}\n")
if verdict == "H-CoverageInvalid":
    raise SystemExit(5)
PY
