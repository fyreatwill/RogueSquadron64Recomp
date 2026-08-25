#!/usr/bin/env python3
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

oracle_path, port_dir, out_dir = map(Path, sys.argv[1:])
phases = ((1024, 0x790400), (1024, 0x790800), (512, 0x6AB400), (512, 0x6AB800))
fields = (0x173C20, 0x171DE0, 0x171F70, 0x173DB0)
pcs = (0x800908D4, 0x8009081C, 0x80090810, 0x8009220C, 0x80090CA4)
named = (
    0x800078EC, 0x800908D4, 0x8009081C, 0x80090810, 0x8009220C,
    0x80090CA4, 0x80094648, 0x8008EC88, 0x80091468, 0x800914A4,
    0x80091564, 0x80091618, 0x8008C9AC, 0x8008CA14, 0x80019B74,
    0x8009B5A8, 0x80092128, 0x80092230, 0x8009231C, 0x80090B68,
    0x80090C28, 0x8009C904, 0x8009D740, 0x8009D7D0,
)

def number(value):
    try:
        return int(value, 0)
    except (TypeError, ValueError):
        return 0

def tsv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))

text = oracle_path.read_text(errors="replace")
watch_hits = {
    int(m.group(1), 16): int(m.group(2))
    for m in re.finditer(r"watch write \[0x([0-9a-f]+),0x[0-9a-f]+\): (\d+) hit", text, re.I)
}
named_hits = {
    int(m.group(1), 16): int(m.group(2))
    for m in re.finditer(r"watch pc \[0x([0-9a-f]+),0x[0-9a-f]+\): (\d+) hit", text, re.I)
}
phase_hist = {
    (int(m.group(2)), int(m.group(1), 16))
    for m in re.finditer(r"pc-hist-phase origin=0x([0-9a-f]+) width=(\d+)", text, re.I)
}
writer_fields = defaultdict(set)
for m in re.finditer(
    r"writer-pc-phase origin=0x([0-9a-f]+) width=(\d+) watch=(\d+) .*?pc=0x([0-9a-f]+)",
    text, re.I,
):
    phase = (int(m.group(2)), int(m.group(1), 16))
    watch = int(m.group(3))
    if phase in phases and watch in (2, 3, 4, 5):
        writer_fields[(phase, int(m.group(4), 16))].add({2: fields[0], 3: fields[1], 4: fields[2], 5: fields[3]}[watch])

field_rows = []
row_re = re.compile(
    r"pc-field-dump\] pc=0x([0-9a-f]+) width=(\d+) origin=0x([0-9a-f]+) "
    r"s0=0x([0-9a-f]+) s1=0x([0-9a-f]+) source_word=0x([0-9a-f]+) "
    r"source_byte=0x([0-9a-f]+) branch_selector=0x([0-9a-f]+) "
    r"branch_state=0x([0-9a-f]+)", re.I
)
for m in row_re.finditer(text):
    phase = (int(m.group(2)), int(m.group(3), 16))
    if phase in phases:
        field_rows.append((phase, int(m.group(1), 16), *(int(m.group(i), 16) for i in range(4, 10))))
summary_overflow = {
    int(m.group(1), 16): int(m.group(3))
    for m in re.finditer(r"pc-field-summary pc=0x([0-9a-f]+) rows=\d+/\d+ hits=\d+ overflow=(\d+)", text, re.I)
}
port_rows = tsv(port_dir / "phase-task-writer-placement-table.tsv")
port_summary = tsv(port_dir / "phase-task-writer-placement-summary.tsv")

def port_for(phase, field):
    return [r for r in port_rows if (number(r.get("width")), number(r.get("origin"))) == phase and number(r.get("field_phys")) == field]

header = [
    "phase", "width", "origin", "writer_pc", "field_phys", "s0", "s1",
    "source_word", "source_byte", "branch_selector", "branch_state",
    "nonzero_match", "zero_only_match", "port_arms", "port_rows", "task_n",
    "field_pre", "field_post", "task_begin", "task_end", "ordering",
]
table = [header]
nonzero_matches = 0
zero_only_matches = 0
for phase, pc, s0, s1, source_word, source_byte, branch_selector, branch_state in field_rows:
    for field in sorted(writer_fields[(phase, pc)] or fields):
        ports = port_for(phase, field)
        port_values = {number(r.get("field_pre")) for r in ports} | {number(r.get("field_post")) for r in ports}
        pointed = {source_word, source_byte, branch_selector, branch_state}
        nz = bool((pointed & port_values) - {0})
        zero = bool(pointed & port_values) and not nz
        nonzero_matches += nz
        zero_only_matches += zero
        table.append([
            f"{phase[0]}:0x{phase[1]:06X}", str(phase[0]), f"0x{phase[1]:06X}",
            f"0x{pc:08X}", f"0x{field:06X}", f"0x{s0:08X}", f"0x{s1:08X}",
            f"0x{source_word:08X}", f"0x{source_byte:02X}",
            f"0x{branch_selector:08X}", f"0x{branch_state:04X}", str(int(nz)),
            str(int(zero)), ",".join(sorted({r.get("arm", "-") for r in ports})) or "-",
            str(len(ports)), ",".join(r.get("task_n", "-") for r in ports) or "-",
            ",".join(r.get("field_pre", "-") for r in ports) or "-",
            ",".join(r.get("field_post", "-") for r in ports) or "-",
            ",".join(r.get("task_begin", "-") for r in ports) or "-",
            ",".join(r.get("task_end", "-") for r in ports) or "-",
            ",".join(r.get("ordering", "-") for r in ports) or "-",
        ])

out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "retail-field-role-table.tsv").write_text(
    "\n".join("\t".join(row) for row in table) + "\n"
)
whole = watch_hits.get(0, 0) > 0
target = watch_hits.get(0x149470, 0) > 0
exact = all(watch_hits.get(field, 0) > 0 for field in fields)
controls = len(port_summary) == 4 and all(row.get("controls") == "1" for row in port_summary)
coverage = whole and target and exact and phase_hist == set(phases) and all(named_hits.get(pc, 0) > 0 for pc in named) and controls
if not coverage:
    verdict = "H-CoverageInvalid"
elif any(summary_overflow.get(pc, 0) for pc in pcs):
    verdict = "H-RetailRoleAmbiguous"
elif nonzero_matches:
    verdict = "H-RetailCandidateFieldsShareVoiceShape"
elif field_rows and zero_only_matches:
    verdict = "H-RetailRoleAmbiguous"
else:
    verdict = "H-RetailCandidateFieldsAreSeparateState"
summary = (
    f"retail_controls={int(coverage)} whole_rdram={watch_hits.get(0, 0)} "
    f"target_window={watch_hits.get(0x149470, 0)} "
    f"exact_fields={','.join(str(watch_hits.get(f, 0)) for f in fields)} "
    f"phase_controls={int(phase_hist == set(phases))} "
    f"named_controls={sum(named_hits.get(pc, 0) > 0 for pc in named)}/{len(named)} "
    f"port_controls={int(controls)} field_rows={len(field_rows)} "
    f"nonzero_matches={nonzero_matches} zero_only_matches={zero_only_matches} verdict={verdict}\n"
)
print(summary, end="")
(out_dir / "summary.txt").write_text(summary)
if verdict == "H-CoverageInvalid":
    raise SystemExit(5)
