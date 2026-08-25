#!/bin/zsh
set -u
set -o pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TAG=${1:-s2353_m5_hangar_field_set}
OUT="$ROOT/scratch/agent/$TAG"
ORACLE="${RS64_ORACLE:-$ROOT/scratch/agent/s2353_m5_hangar_field_set_oracle.log}"
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
hangar_phase = {(512, 0x6AB400), (512, 0x6AB800)}
watch_fields = {
    2: 0x173C20,
    3: 0x171DE0,
    4: 0x171F70,
    5: 0x173DB0,
}
named_controls = (
    0x800078EC, 0x800908D4, 0x8009081C, 0x80090810, 0x80090CA4,
    0x80094648, 0x8008EC88, 0x80091468, 0x800914A4, 0x80091564,
    0x80091618, 0x8008C9AC, 0x8008CA14, 0x80019B74, 0x8009B5A8,
    0x80092128, 0x80092230, 0x8009231C, 0x80090B68, 0x80090C28,
    0x8009C904, 0x8009D740, 0x8009D7D0,
)

def n(value):
    try:
        return int(value, 0)
    except (TypeError, ValueError):
        return 0

text = oracle_path.read_text(errors="replace")
watch_hits = {}
for match in re.finditer(r"watch write \[0x([0-9a-f]+),0x[0-9a-f]+\): (\d+) hit", text, re.I):
    watch_hits[int(match.group(1), 16)] = int(match.group(2))

phase_hist = set()
for match in re.finditer(r"pc-hist-phase origin=0x([0-9a-f]+) width=(\d+)", text, re.I):
    phase = (int(match.group(2)), int(match.group(1), 16))
    if phase in phases:
        phase_hist.add(phase)

writer_pcs = defaultdict(lambda: defaultdict(int))
for match in re.finditer(
        r"writer-pc-phase origin=0x([0-9a-f]+) width=(\d+) watch=(\d+) .*pc=0x([0-9a-f]+) n=(\d+)",
        text, re.I):
    phase = (int(match.group(2)), int(match.group(1), 16))
    watch = int(match.group(3))
    if phase in phases and watch in watch_fields:
        writer_pcs[(phase, watch)][int(match.group(4), 16)] += int(match.group(5))

post_rows = defaultdict(int)
for match in re.finditer(
        r"post-value-pc-row pc=0x([0-9a-f]+) .*width=(\d+) origin=0x([0-9a-f]+) addr=0x([0-9a-f]+)",
        text, re.I):
    phase = (int(match.group(2)), int(match.group(3), 16))
    addr = int(match.group(4), 16)
    if phase in phases and addr in watch_fields.values():
        post_rows[(phase, addr)] += 1

named_hits = {}
for match in re.finditer(r"watch pc \[0x([0-9a-f]+),0x[0-9a-f]+\): (\d+) hit", text, re.I):
    named_hits[int(match.group(1), 16)] = int(match.group(2))

def read_tsv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))

port_rows = read_tsv(port_dir / "phase-task-writer-placement-table.tsv")
port_summary = read_tsv(port_dir / "phase-task-writer-placement-summary.tsv")
port_hangar_fields_all = {
    n(row.get("field_phys"))
    for row in port_rows
    if n(row.get("width")) == 512 and n(row.get("origin")) == 0x6AB400
}
expected_hangar_fields = {watch_fields[i] for i in (3, 4, 5)}
port_hangar_fields = port_hangar_fields_all & expected_hangar_fields
port_controls = all(
    row.get("controls") == "1" and row.get("title", "0") != "0" and row.get("hangar", "0") != "0"
    for row in port_summary
) and len(port_summary) == 4 and expected_hangar_fields <= port_hangar_fields

header = [
    "phase", "width", "origin", "watch", "field_phys", "global_watch_hits",
    "writer_pc", "writer_rows", "post_rows", "port_hangar_field", "port_rows",
    "phase_hist", "named_pc_controls", "s2352_port_controls",
]
table = [header]
for phase in phases:
    for watch, field in watch_fields.items():
        pcs = writer_pcs[(phase, watch)]
        matching_port_rows = sum(
            n(row.get("field_phys")) == field and
            n(row.get("width")) == phase[0] and
            n(row.get("origin")) == phase[1]
            for row in port_rows
        )
        items = sorted(pcs.items()) or [(0, 0)]
        for pc, rows in items:
            table.append([
                f"{phase[0]}:0x{phase[1]:06X}", str(phase[0]), f"0x{phase[1]:06X}",
                str(watch), f"0x{field:06X}", str(watch_hits.get(field, 0)),
                f"0x{pc:08X}" if pc else "-", str(rows), str(post_rows[(phase, field)]),
                str(int(field in port_hangar_fields)), str(matching_port_rows),
                str(int(phase in phase_hist)),
                f"{sum(named_hits.get(pc, 0) > 0 for pc in named_controls)}/{len(named_controls)}",
                str(int(port_controls)),
            ])

(out_dir / "retail-hangar-field-writer-table.tsv").write_text(
    "\n".join("\t".join(row) for row in table) + "\n"
)
(out_dir / "retail-hangar-field-writer-summary.tsv").write_text(
    "phase\twatch\tfield_phys\twriter_pcs\tglobal_hits\tpost_rows\tport_hangar_field\n" +
    "\n".join(
        f"{width}:{origin:06X}\t{watch}\t0x{field:06X}\t" +
        (",".join(f"0x{pc:08X}:{rows}" for pc, rows in sorted(writer_pcs[((width, origin), watch)].items())) or "-") +
        f"\t{watch_hits.get(field, 0)}\t{post_rows[((width, origin), field)]}\t{int(field in port_hangar_fields)}"
        for width, origin in phases for watch, field in watch_fields.items()
    ) + "\n"
)

whole = watch_hits.get(0, 0) > 0
target = watch_hits.get(0x149470, 0) > 0
exact = all(watch_hits.get(field, 0) > 0 for field in watch_fields.values())
phases_ok = len(phase_hist) == len(phases)
named_ok = all(named_hits.get(pc, 0) > 0 for pc in named_controls)
positive_hangar_matches = [
    (phase, watch, pc, rows)
    for phase in hangar_phase
    for watch in (3, 4, 5)
    for pc, rows in writer_pcs[(phase, watch)].items()
    if rows > 0 and watch_fields[watch] in port_hangar_fields
]
positive_hangar_outside = [
    (phase, watch, pc, rows)
    for phase in hangar_phase
    for watch in (3, 4, 5)
    for pc, rows in writer_pcs[(phase, watch)].items()
    if rows > 0 and watch_fields[watch] not in port_hangar_fields
]
all_hangar_empty = all(not writer_pcs[(phase, watch)] for phase in hangar_phase for watch in (3, 4, 5))

print(
    f"retail_controls={int(whole and target and exact and phases_ok and named_ok)} "
    f"whole_rdram={watch_hits.get(0, 0)} target_window={watch_hits.get(0x149470, 0)} "
    f"exact_fields={int(exact)} phase_controls={int(phases_ok)} "
    f"named_controls={sum(named_hits.get(pc, 0) > 0 for pc in named_controls)}/{len(named_controls)} "
    f"port_hangar_fields={','.join(f'0x{x:06X}' for x in sorted(port_hangar_fields)) or '-'} "
    f"port_controls={int(port_controls)}"
)
for phase in phases:
    print(
        f"phase={phase[0]}:{phase[1]:06X} hist={int(phase in phase_hist)} "
        + " ".join(
            f"watch{watch}=" + (",".join(f"0x{pc:08X}:{rows}" for pc, rows in sorted(writer_pcs[(phase, watch)].items())) or "-")
            for watch in (2, 3, 4, 5)
        )
    )
print(f"hangar_matches={len(positive_hangar_matches)} outside={len(positive_hangar_outside)}")
if not (whole and target and exact and phases_ok and named_ok and port_controls):
    verdict = "H-CoverageInvalid"
elif positive_hangar_matches:
    verdict = "H-HangarFieldWriterInPortSet"
elif positive_hangar_outside:
    verdict = "H-HangarFieldSetMismatch"
elif all_hangar_empty:
    verdict = "H-HangarFieldsOutsidePhase"
else:
    verdict = "H-CoverageInvalid"
print(f"verdict={verdict}")
if verdict == "H-CoverageInvalid":
    raise SystemExit(5)
PY
