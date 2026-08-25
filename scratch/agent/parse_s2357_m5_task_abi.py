#!/usr/bin/env python3
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

oracle_path, port_dir, out_dir = map(Path, sys.argv[1:])
phases = ((1024, 0x790400), (1024, 0x790800), (512, 0x6AB400), (512, 0x6AB800))
fields = (0x173C20, 0x171DE0, 0x171F70, 0x173DB0)
named = (
    0x800078EC, 0x80033FCC, 0x800908D4, 0x8009081C, 0x80090810,
    0x8009220C, 0x80090CA4, 0x80094648, 0x8008EC88, 0x80091468,
    0x800914A4, 0x80091564, 0x80091618, 0x8008C9AC, 0x8008CA14,
    0x80019B74, 0x8009B5A8, 0x80092128, 0x80092230, 0x8009231C,
    0x80090B68, 0x80090C28, 0x8009C904, 0x8009D740, 0x8009D7D0,
)


def number(value):
    try:
        return int(value, 0)
    except (TypeError, ValueError):
        return 0


def tsv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def values(rows, key):
    return sorted({row.get(key, "-") for row in rows})


def joined(items):
    return ",".join(str(item) for item in items) if items else "-"


text = oracle_path.read_text(errors="replace")
watch_hits = {
    int(m.group(1), 16): int(m.group(2))
    for m in re.finditer(
        r"watch write \[0x([0-9a-f]+),0x[0-9a-f]+\): (\d+) hit", text, re.I
    )
}
named_hits = {
    int(m.group(1), 16): int(m.group(2))
    for m in re.finditer(
        r"watch pc \[0x([0-9a-f]+),0x[0-9a-f]+\): (\d+) hit", text, re.I
    )
}
phase_hist = {
    (int(m.group(2)), int(m.group(1), 16))
    for m in re.finditer(r"pc-hist-phase origin=0x([0-9a-f]+) width=(\d+)", text, re.I)
}
hist_watches = {
    int(m.group(1))
    for m in re.finditer(
        r"writer-pc-phase origin=0x[0-9a-f]+ width=\d+ watch=(\d+) range=",
        text, re.I,
    )
}
watch_to_field = {2: fields[0], 3: fields[1], 4: fields[2], 5: fields[3]}
writer_by_field = defaultdict(lambda: defaultdict(int))
for m in re.finditer(
    r"writer-pc-phase origin=0x([0-9a-f]+) width=(\d+) watch=(\d+) .*?"
    r"pc=0x([0-9a-f]+) n=(\d+)", text, re.I,
):
    phase = (int(m.group(2)), int(m.group(1), 16))
    watch = int(m.group(3))
    if phase in phases and watch in watch_to_field:
        writer_by_field[(phase, watch_to_field[watch])][int(m.group(4), 16)] += int(m.group(5))

task_re = re.compile(
    r"^\[pc-task-dump\] pc=0x([0-9a-f]+) width=(\d+) origin=0x([0-9a-f]+) "
    r"task_n=(\d+) task_ptr=0x([0-9a-f]+) task_phys=0x([0-9a-f]+) "
    r"type=0x([0-9a-f]+) data_ptr=0x([0-9a-f]+) data_size=0x([0-9a-f]+) "
    r"output_buff=0x([0-9a-f]+) output_buff_size=0x([0-9a-f]+) "
    r"yield_data_ptr=0x([0-9a-f]+) yield_data_size=0x([0-9a-f]+) "
    r"data_ptr_plus_100=0x([0-9a-f]+) field_phys=0x([0-9a-f]+)$",
    re.I | re.M,
)
task_rows = []
for match in task_re.finditer(text):
    values_row = [int(match.group(i), 16) for i in (1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)]
    task_rows.append({
        "pc": values_row[0],
        "width": int(match.group(2)),
        "origin": values_row[1],
        "task_n": int(match.group(4)),
        "task_ptr": values_row[2],
        "task_phys": values_row[3],
        "type": values_row[4],
        "data_ptr": values_row[5],
        "data_size": values_row[6],
        "output_buff": values_row[7],
        "output_buff_size": values_row[8],
        "yield_data_ptr": values_row[9],
        "yield_data_size": values_row[10],
        "data_ptr_plus_100": values_row[11],
        "field_phys": values_row[12],
    })

summary_match = re.search(
    r"pc-task-summary pc=0x([0-9a-f]+) rows=(\d+)/(\d+) phase_hits=(\d+) "
    r"type2=(\d+) non_type2=(\d+) invalid=(\d+) overflow=(\d+)", text, re.I
)
task_summary = {
    "pc": int(summary_match.group(1), 16),
    "rows": int(summary_match.group(2)),
    "capacity": int(summary_match.group(3)),
    "phase_hits": int(summary_match.group(4)),
    "type2": int(summary_match.group(5)),
    "non_type2": int(summary_match.group(6)),
    "invalid": int(summary_match.group(7)),
    "overflow": int(summary_match.group(8)),
} if summary_match else None

port_rows = tsv(port_dir / "phase-task-writer-placement-table.tsv")
port_summary = tsv(port_dir / "phase-task-writer-placement-summary.tsv")


def port_for(phase, field):
    return [
        row for row in port_rows
        if (number(row.get("width")), number(row.get("origin"))) == phase
        and number(row.get("field_phys")) == field
    ]


header = [
    "phase", "width", "origin", "task_n", "task_ptr", "task_phys", "type",
    "data_ptr", "data_size", "output_buff", "output_buff_size", "yield_data_ptr",
    "yield_data_size", "data_ptr_plus_100", "field_phys", "retail_writer_pcs",
    "retail_writer_rows", "port_arms", "port_rows", "port_task_range",
    "field_pre", "field_post", "field_changed", "field_write_event",
    "ordering", "nonzero_task_field_relation", "zero_sentinel_only",
]
table = [header]
nonzero_relations = 0
zero_sentinel_only = 0
for row in task_rows:
    phase = (row["width"], row["origin"])
    field = row["field_phys"]
    writers = writer_by_field.get((phase, field), {})
    ports = port_for(phase, field)
    port_nonzero = any(
        number(port.get("field_pre")) != 0 or number(port.get("field_post")) != 0
        for port in ports
    )
    relation = bool(field in fields and writers and ports and port_nonzero)
    task_zero = all(
        row[key] == 0
        for key in ("output_buff", "output_buff_size", "yield_data_ptr", "yield_data_size")
    )
    zero_only = bool(field in fields and task_zero and not relation)
    nonzero_relations += int(relation)
    zero_sentinel_only += int(zero_only)
    task_numbers = [number(port.get("task_n")) for port in ports]
    table.append([
        f"{row['width']}:0x{row['origin']:06X}", str(row["width"]),
        f"0x{row['origin']:06X}", str(row["task_n"]),
        f"0x{row['task_ptr']:08X}", f"0x{row['task_phys']:06X}",
        f"0x{row['type']:08X}", f"0x{row['data_ptr']:08X}",
        f"0x{row['data_size']:08X}", f"0x{row['output_buff']:08X}",
        f"0x{row['output_buff_size']:08X}", f"0x{row['yield_data_ptr']:08X}",
        f"0x{row['yield_data_size']:08X}", f"0x{row['data_ptr_plus_100']:08X}",
        f"0x{field:06X}", joined(f"0x{pc:08X}" for pc in sorted(writers)),
        str(sum(writers.values())), joined(sorted({port.get("arm", "-") for port in ports})),
        str(len(ports)),
        f"{min(task_numbers)}..{max(task_numbers)}" if task_numbers else "-",
        joined(sorted(set(port.get("field_pre", "-") for port in ports))),
        joined(sorted(set(port.get("field_post", "-") for port in ports))),
        joined(sorted(set(port.get("field_changed", "-") for port in ports))),
        joined(sorted(set(port.get("field_write_event", "-") for port in ports))),
        joined(sorted(set(port.get("ordering", "-") for port in ports))),
        str(int(relation)), str(int(zero_only)),
    ])

out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "retail-task-abi-field-relation-table.tsv").write_text(
    "\n".join("\t".join(row) for row in table) + "\n"
)
whole = watch_hits.get(0, 0) > 0
target = watch_hits.get(0x149470, 0) > 0
exact = all(watch_hits.get(field, 0) > 0 for field in fields)
phase_controls = phase_hist == set(phases)
named_controls = all(named_hits.get(pc, 0) > 0 for pc in named)
hist_controls = hist_watches == {2, 3, 4, 5}
port_controls = len(port_summary) == 4 and all(row.get("controls") == "1" for row in port_summary)
task_controls = bool(
    task_summary and task_summary["pc"] == 0x80033FCC
    and task_summary["phase_hits"] > 0
    and task_summary["type2"] > 0
    and task_summary["rows"] == len(task_rows)
    and task_summary["rows"] == task_summary["type2"]
    and task_summary["invalid"] == 0
    and task_summary["overflow"] == 0
)
coverage = (
    whole and target and exact and phase_controls and named_controls
    and hist_controls and port_controls and task_controls
)
if not coverage:
    verdict = "H-CoverageInvalid"
elif nonzero_relations:
    verdict = "H-RetailTaskAbiNamesPortField"
else:
    verdict = "H-RetailTaskAbiUsesSeparateBuffer"
summary = (
    f"retail_controls={int(coverage)} whole_rdram={watch_hits.get(0, 0)} "
    f"target_window={watch_hits.get(0x149470, 0)} "
    f"exact_fields={','.join(str(watch_hits.get(field, 0)) for field in fields)} "
    f"phase_controls={int(phase_controls)} hist_watches={','.join(str(w) for w in sorted(hist_watches))} "
    f"named_controls={sum(named_hits.get(pc, 0) > 0 for pc in named)}/{len(named)} "
    f"port_controls={int(port_controls)} task_rows={len(task_rows)} "
    f"task_phase_hits={task_summary['phase_hits'] if task_summary else 0} "
    f"task_type2={task_summary['type2'] if task_summary else 0} "
    f"task_overflow={task_summary['overflow'] if task_summary else 0} "
    f"nonzero_task_field_relations={nonzero_relations} "
    f"zero_sentinel_only={zero_sentinel_only} verdict={verdict}\n"
)
print(summary, end="")
(out_dir / "summary.txt").write_text(summary)
if verdict == "H-CoverageInvalid":
    raise SystemExit(5)
