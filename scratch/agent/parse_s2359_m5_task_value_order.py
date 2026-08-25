#!/usr/bin/env python3
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

oracle_path, port_dir, out_dir = map(Path, sys.argv[1:])
phases = ((1024, 0x790400), (1024, 0x790800), (512, 0x6AB400), (512, 0x6AB800))
fields = (0x173C20, 0x171DE0, 0x171F70, 0x173DB0)
watch_to_field = {2: fields[0], 3: fields[1], 4: fields[2], 5: fields[3]}
writer_pc = 0x80090CA4
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


def hex_value(value):
    return f"0x{value:08X}"


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
        r"writer-pc-phase origin=0x[0-9a-f]+ width=\d+ watch=(\d+) range=", text, re.I
    )
}

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
    task_rows.append({
        "pc": int(match.group(1), 16),
        "width": int(match.group(2)),
        "origin": int(match.group(3), 16),
        "task_n": int(match.group(4)),
        "task_ptr": int(match.group(5), 16),
        "task_phys": int(match.group(6), 16),
        "type": int(match.group(7), 16),
        "data_ptr": int(match.group(8), 16),
        "data_size": int(match.group(9), 16),
        "output_buff": int(match.group(10), 16),
        "output_buff_size": int(match.group(11), 16),
        "yield_data_ptr": int(match.group(12), 16),
        "yield_data_size": int(match.group(13), 16),
        "data_ptr_plus_100": int(match.group(14), 16),
        "field_phys": int(match.group(15), 16),
    })

task_scope = defaultdict(list)
for row in task_rows:
    task_scope[(row["width"], row["origin"], row["field_phys"])].append(row["task_n"])

post_re = re.compile(
    r"post-value-pc-row pc=0x([0-9a-f]+) vi=(\d+) width=(\d+) "
    r"origin=0x([0-9a-f]+) addr=0x([0-9a-f]+) value=0x([0-9a-f]+)", re.I
)
post_rows = [
    {
        "pc": int(m.group(1), 16),
        "vi": int(m.group(2)),
        "width": int(m.group(3)),
        "origin": int(m.group(4), 16),
        "field": int(m.group(5), 16),
        "value": int(m.group(6), 16),
    }
    for m in post_re.finditer(text)
]

post_detail_summaries = {
    (int(m.group(1)), int(m.group(2), 16)): {
        "samples": int(m.group(3)),
        "zero": int(m.group(4)),
        "nonzero": int(m.group(5)),
    }
    for m in re.finditer(
        r"post-value-pc watch=(\d+) pc=0x([0-9a-f]+) samples=(\d+) "
        r"zero=(\d+) nonzero=(\d+)", text, re.I
    )
}
post_detail_counts = Counter(
    (next((watch for watch, field in watch_to_field.items() if field == row["field"]), 0), row["pc"])
    for row in post_rows
)
post_detail_overflows = [
    int(m.group(1))
    for m in re.finditer(r"post-value-pc .*?overflow=(\d+)", text, re.I)
]
post_hist_overflows = [
    int(m.group(1))
    for m in re.finditer(r"post-value watch=\d+ .*?overflow=(\d+)", text, re.I)
]
target_sequence_overflow = next(
    (int(m.group(1)) for m in re.finditer(r"post-target-sequence n=\d+/\d+ overflow=(\d+)", text, re.I)),
    0,
)

writer_hist = defaultdict(int)
for match in re.finditer(
    r"writer-pc-phase origin=0x([0-9a-f]+) width=(\d+) watch=(\d+) "
    r"pc=0x([0-9a-f]+) n=(\d+)", text, re.I
):
    phase = (int(match.group(2)), int(match.group(1), 16))
    field = watch_to_field.get(int(match.group(3)))
    if field is not None:
        writer_hist[(phase, field, int(match.group(4), 16))] += int(match.group(5))

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
port_profiles = defaultdict(set)
for row in port_rows:
    phase = (number(row.get("width")), number(row.get("origin")))
    field = number(row.get("field_phys"))
    if phase in phases and field in fields:
        port_profiles[(phase, field)].add((
            row.get("arm", "-"),
            row.get("field_pre", "-"),
            row.get("field_post", "-"),
            row.get("ordering", "-"),
        ))

task_field_keys = set(task_scope)
task_phase_keys = {key[:2] for key in task_field_keys}
post_task_rows = [
    row for row in post_rows
    if row["pc"] == writer_pc
    and (row["width"], row["origin"]) in phases
    and (row["width"], row["origin"], row["field"]) in task_scope
]
post_task_keys = {(row["width"], row["origin"], row["field"]) for row in post_task_rows}
post_task_by_key = defaultdict(list)
for row in post_task_rows:
    post_task_by_key[(row["width"], row["origin"], row["field"])].append(row)

table = [[
    "phase", "width", "origin", "task_n", "field_phys", "writer_pc", "writer_vi",
    "writer_value", "port_arm", "field_pre", "field_post", "ordering",
    "task_rows", "task_n_min", "task_n_max", "writer_hist_rows", "value_class",
]]
value_matches = 0
value_mismatches = 0
zero_sentinel_only = 0
no_port_profile = 0
for key in sorted(post_task_by_key):
    width, origin, field = key
    task_numbers = sorted(task_scope[key])
    profiles = sorted(port_profiles.get(((width, origin), field), ()))
    if not profiles:
        profiles = [("-", "-", "-", "-")]
        no_port_profile += len(post_task_by_key[key])
    expected = {
        number(value)
        for profile in profiles
        for value in profile[1:3]
        if number(value) != 0
    }
    for post in post_task_by_key[key]:
        if not expected:
            value_class = "zero_or_no_payload" if post["value"] == 0 else "no_port_payload"
        elif post["value"] == 0:
            value_class = "zero_or_sentinel"
            zero_sentinel_only += 1
        elif post["value"] in expected:
            value_class = "value_match"
            value_matches += 1
        else:
            value_class = "value_mismatch"
            value_mismatches += 1
        for arm, field_pre, field_post, ordering in profiles:
            table.append([
                f"{width}:0x{origin:06X}", str(width), f"0x{origin:06X}",
                f"{task_numbers[0]}..{task_numbers[-1]}" if task_numbers[0] != task_numbers[-1] else str(task_numbers[0]),
                f"0x{field:06X}", hex_value(post["pc"]), str(post["vi"]),
                hex_value(post["value"]), arm, field_pre, field_post, ordering,
                str(len(task_numbers)), str(task_numbers[0]), str(task_numbers[-1]),
                str(writer_hist.get(((width, origin), field, writer_pc), 0)),
                value_class,
            ])

out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "retail-task-value-order-table.tsv").write_text(
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
    task_summary
    and task_summary["pc"] == 0x80033FCC
    and task_summary["phase_hits"] > 0
    and task_summary["type2"] > 0
    and task_summary["rows"] == len(task_rows)
    and task_summary["rows"] == task_summary["type2"]
    and task_summary["invalid"] == 0
    and task_summary["overflow"] == 0
)
detail_controls = all(
    (watch, writer_pc) in post_detail_summaries
    and post_detail_summaries[(watch, writer_pc)]["samples"] == post_detail_counts[(watch, writer_pc)]
    for watch in watch_to_field
)
writer_controls = all(
    writer_hist.get(((width, origin), field, writer_pc), 0) > 0
    for width, origin, field in task_field_keys
    if (width, origin) in phases and field in fields
)
coverage = (
    whole and target and exact and phase_controls and named_controls and hist_controls
    and port_controls and task_controls and detail_controls and writer_controls
    and len(task_phase_keys) == len(phases)
)

if not coverage:
    verdict = "H-CoverageInvalid"
elif not post_task_rows:
    verdict = "H-RetailWriterPostValueAbsent"
elif value_mismatches:
    verdict = "H-RetailWriterPayloadMismatch"
elif value_matches and not no_port_profile:
    verdict = "H-RetailWriterPublishesTaskField"
else:
    verdict = "H-RetailWriterPayloadUnresolved"

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
    f"task_field_keys={len(task_field_keys)} writer_task_keys={sum(writer_hist.get((key[:2], key[2], writer_pc), 0) > 0 for key in task_field_keys)} "
    f"post_detail_controls={int(detail_controls)} post_detail_overflow={sum(post_detail_overflows)} "
    f"post_histogram_overflow={sum(post_hist_overflows)} target_sequence_overflow={target_sequence_overflow} "
    f"post_task_rows={len(post_task_rows)} post_task_keys={len(post_task_keys)} "
    f"value_matches={value_matches} value_mismatches={value_mismatches} "
    f"zero_sentinel_only={zero_sentinel_only} no_port_profile_rows={no_port_profile} "
    f"task_n_join=phase_field_scope_only verdict={verdict}\n"
)
print(summary, end="")
(out_dir / "summary.txt").write_text(summary)
if verdict == "H-CoverageInvalid":
    raise SystemExit(5)
