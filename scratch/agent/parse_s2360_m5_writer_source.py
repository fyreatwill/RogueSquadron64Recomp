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


def hex_value(value):
    return f"0x{value:08X}"


def tsv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


watch_hits = {}
named_hits = {}
phase_hist = set()
hist_watches = set()
task_rows = []
post_rows = []
writer_rows = defaultdict(Counter)
writer_counts = Counter()
post_counts = Counter()
post_detail_counts = Counter()
post_detail_overflows = []
post_hist_overflows = []
task_summary = None
detail_overflow = 0

task_re = re.compile(
    r"^\[pc-task-dump\] pc=0x([0-9a-f]+) width=(\d+) origin=0x([0-9a-f]+) "
    r"task_n=(\d+) task_ptr=0x([0-9a-f]+) task_phys=0x([0-9a-f]+) "
    r"type=0x([0-9a-f]+) data_ptr=0x([0-9a-f]+) data_size=0x([0-9a-f]+) "
    r"output_buff=0x([0-9a-f]+) output_buff_size=0x([0-9a-f]+) "
    r"yield_data_ptr=0x([0-9a-f]+) yield_data_size=0x([0-9a-f]+) "
    r"data_ptr_plus_100=0x([0-9a-f]+) field_phys=0x([0-9a-f]+)$",
    re.I,
)
writer_re = re.compile(
    r"^\[hit\] x addr=0x[0-9a-f]+ pc=0x80090ca4 .*?"
    r"s1=0x([0-9a-f]+) a0=0x([0-9a-f]+) a1=0x([0-9a-f]+) "
    r"a2=0x([0-9a-f]+) s0=0x([0-9a-f]+) width=(\d+) origin=0x([0-9a-f]+)$",
    re.I,
)
post_re = re.compile(
    r"^\[oracle\] post-value-pc-row pc=0x([0-9a-f]+) vi=(\d+) width=(\d+) "
    r"origin=0x([0-9a-f]+) addr=0x([0-9a-f]+) value=0x([0-9a-f]+)$",
    re.I,
)

with oracle_path.open(errors="replace") as stream:
    for line in stream:
        line = line.rstrip("\n")
        match = re.search(r"watch write \[0x([0-9a-f]+),0x[0-9a-f]+\): (\d+) hit", line, re.I)
        if match:
            watch_hits[int(match.group(1), 16)] = int(match.group(2))
        match = re.search(r"watch pc \[0x([0-9a-f]+),0x[0-9a-f]+\): (\d+) hit", line, re.I)
        if match:
            named_hits[int(match.group(1), 16)] = int(match.group(2))
        match = re.search(r"pc-hist-phase origin=0x([0-9a-f]+) width=(\d+)", line, re.I)
        if match:
            phase_hist.add((int(match.group(2)), int(match.group(1), 16)))
        match = re.search(r"writer-pc-phase origin=0x[0-9a-f]+ width=\d+ watch=(\d+) range=", line, re.I)
        if match:
            hist_watches.add(int(match.group(1)))
        match = task_re.match(line)
        if match:
            groups = match.groups()
            values = [int(groups[0], 16), int(groups[1]), int(groups[2], 16), int(groups[3])]
            values.extend(int(value, 16) for value in groups[4:])
            task_rows.append(dict(zip(
                ("pc", "width", "origin", "task_n", "task_ptr", "task_phys", "type",
                 "data_ptr", "data_size", "output_buff", "output_buff_size", "yield_data_ptr",
                 "yield_data_size", "data_ptr_plus_100", "field_phys"), values
            )))
        match = writer_re.match(line)
        if match:
            s1, a0, a1, a2, s0, width, origin = [int(value, 16) for value in match.groups()[:5]] + [
                int(match.group(6)), int(match.group(7), 16)
            ]
            phase = (width, origin)
            if phase in phases:
                writer_counts[phase] += 1
                writer_rows[phase][(s1, a0, a1, a2, s0)] += 1
        match = post_re.match(line)
        if match:
            groups = match.groups()
            pc, vi, width, origin, field, value = (
                int(groups[0], 16), int(groups[1]), int(groups[2]), int(groups[3], 16),
                int(groups[4], 16), int(groups[5], 16)
            )
            row = {"pc": pc, "vi": vi, "width": width, "origin": origin, "field": field, "value": value}
            post_rows.append(row)
            if (width, origin) in phases:
                post_counts[(width, origin, field)] += 1
        match = re.search(r"post-value-pc watch=(\d+) pc=0x([0-9a-f]+) samples=(\d+) zero=(\d+) nonzero=(\d+)", line, re.I)
        if match:
            watch, pc, samples = int(match.group(1)), int(match.group(2), 16), int(match.group(3))
            post_detail_counts[(watch, pc)] = samples
        match = re.search(r"post-value-pc watch=\d+ overflow=(\d+)", line, re.I)
        if match:
            post_detail_overflows.append(int(match.group(1)))
        match = re.search(r"post-value watch=\d+ .* overflow=(\d+)", line, re.I)
        if match:
            post_hist_overflows.append(int(match.group(1)))
        match = re.search(
            r"pc-task-summary pc=0x([0-9a-f]+) rows=(\d+)/(\d+) phase_hits=(\d+) "
            r"type2=(\d+) non_type2=(\d+) invalid=(\d+) overflow=(\d+)", line, re.I
        )
        if match:
            task_summary = dict(zip(
                ("pc", "rows", "capacity", "phase_hits", "type2", "non_type2", "invalid", "overflow"),
                [int(value, 16) if index == 0 else int(value) for index, value in enumerate(match.groups())],
            ))
        match = re.search(r"post-value-pc-detail-overflow n=(\d+)", line, re.I)
        if match:
            detail_overflow = int(match.group(1))

task_scope = defaultdict(list)
for row in task_rows:
    task_scope[(row["width"], row["origin"], row["field_phys"])].append(row["task_n"])

task_by_phase = defaultdict(set)
for row in task_rows:
    task_by_phase[(row["width"], row["origin"])].add((row["data_ptr"], row["data_ptr_plus_100"], row["field_phys"]))

port_summary = tsv(port_dir / "phase-task-writer-placement-summary.tsv")
port_controls = len(port_summary) == 4 and all(row.get("controls") == "1" for row in port_summary)

source_rows = [[
    "phase", "width", "origin", "writer_pc", "source_s1", "source_a0", "source_a1", "source_a2", "source_s0",
    "source_count", "task_field", "data_ptr", "data_ptr_plus_100", "source_register_matches", "source_class",
]]
phase_source_summary = []
for phase in phases:
    candidates = sorted(task_by_phase.get(phase, ()))
    if len(candidates) != 1:
        raise SystemExit(f"expected one task field candidate for {phase}, got {candidates}")
    data_ptr, field_ptr, field = candidates[0]
    direct = Counter()
    rows = writer_rows[phase]
    for values, count in rows.items():
        s1, a0, a1, a2, s0 = values
        matches = []
        if s1 == data_ptr:
            matches.append("s1=data_ptr")
        if s1 == field_ptr:
            matches.append("s1=data_ptr_plus_100")
        if a0 == data_ptr:
            matches.append("a0=data_ptr")
        if a0 == field_ptr:
            matches.append("a0=data_ptr_plus_100")
        if a2 == data_ptr:
            matches.append("a2=data_ptr")
        if a2 == field_ptr:
            matches.append("a2=data_ptr_plus_100")
        if a1 == data_ptr:
            matches.append("a1=data_ptr")
        if a1 == field_ptr:
            matches.append("a1=data_ptr_plus_100")
        if s0 == data_ptr:
            matches.append("s0=data_ptr")
        if s0 == field_ptr:
            matches.append("s0=data_ptr_plus_100")
        if matches:
            for match in matches:
                direct[match] += count
            source_class = "task_data_direct"
        else:
            source_class = "unresolved_non_direct"
        source_rows.append([
            f"{phase[0]}:0x{phase[1]:06X}", str(phase[0]), hex_value(phase[1]), hex_value(writer_pc),
            hex_value(s1), hex_value(a0), hex_value(a1), hex_value(a2), hex_value(s0), str(count),
            hex_value(field), hex_value(data_ptr), hex_value(field_ptr), ",".join(matches) or "-", source_class,
        ])
    phase_source_summary.append((phase, field, data_ptr, field_ptr, writer_counts[phase], direct, len(rows)))

joined_rows = [[
    "phase", "width", "origin", "writer_vi", "writer_pc", "writer_addr", "writer_value", "task_field",
    "data_ptr", "data_ptr_plus_100", "task_n_scope", "source_class", "source_join_scope",
]]
for row in post_rows:
    phase = (row["width"], row["origin"])
    if phase not in phases:
        continue
    candidates = [candidate for candidate in task_by_phase[phase] if candidate[2] == row["field"]]
    if not candidates:
        continue
    data_ptr, field_ptr, field = candidates[0]
    task_numbers = task_scope[(row["width"], row["origin"], row["field"])]
    direct = phase_source_summary[phases.index(phase)][5]
    source_class = "task_data_direct" if direct else "unresolved_non_direct"
    joined_rows.append([
        f"{phase[0]}:0x{phase[1]:06X}", str(row["width"]), hex_value(row["origin"]), str(row["vi"]),
        hex_value(row["pc"]), hex_value(row["field"]), hex_value(row["value"]), hex_value(field),
        hex_value(data_ptr), hex_value(field_ptr), f"{min(task_numbers)}..{max(task_numbers)}",
        source_class, "phase_field_scope_only",
    ])

out_dir.mkdir(parents=True, exist_ok=True)
with (out_dir / "writer-source-table.tsv").open("w", newline="") as stream:
    csv.writer(stream, delimiter="\t", lineterminator="\n").writerows(source_rows)
with (out_dir / "writer-source-join-table.tsv").open("w", newline="") as stream:
    csv.writer(stream, delimiter="\t", lineterminator="\n").writerows(joined_rows)

whole = watch_hits.get(0, 0) > 0
target = watch_hits.get(0x149470, 0) > 0
exact = all(watch_hits.get(field, 0) > 0 for field in fields)
phase_controls = phase_hist == set(phases)
named_controls = all(named_hits.get(pc, 0) > 0 for pc in named)
hist_controls = hist_watches == {2, 3, 4, 5}
task_controls = bool(
    task_summary and task_summary["pc"] == 0x80033FCC and task_summary["rows"] == len(task_rows)
    and task_summary["rows"] == task_summary["type2"] and task_summary["phase_hits"] > 0
    and task_summary["invalid"] == 0 and task_summary["overflow"] == 0
)
post_phase_rows = [row for row in post_rows if (row["width"], row["origin"]) in phases]
post_task_rows = [row for row in post_phase_rows if (row["width"], row["origin"], row["field"]) in task_scope]
detail_controls = detail_overflow == 0 and all(
    (watch, writer_pc) in post_detail_counts for watch in watch_to_field
)
source_controls = all(writer_counts[phase] > 0 and summary[4] for phase, *summary in phase_source_summary)
coverage = whole and target and exact and phase_controls and named_controls and hist_controls and port_controls and task_controls and detail_controls and source_controls
source_direct_rows = sum(sum(direct.values()) for _, _, _, _, _, direct, _ in phase_source_summary)
source_direct_keys = sum(bool(direct) for _, _, _, _, _, direct, _ in phase_source_summary)
verdict = "H-CoverageInvalid" if not coverage else "H-RetailWriterSourceIsTaskData"

lines = []
lines.append(
    f"retail_controls={int(coverage)} whole_rdram={watch_hits.get(0, 0)} target_window={watch_hits.get(0x149470, 0)} "
    f"exact_fields={','.join(str(watch_hits.get(field, 0)) for field in fields)} phase_controls={int(phase_controls)} "
    f"hist_watches={','.join(str(watch) for watch in sorted(hist_watches))} named_controls={sum(named_hits.get(pc, 0) > 0 for pc in named)}/{len(named)} "
    f"port_controls={int(port_controls)} task_rows={len(task_rows)} task_phase_hits={task_summary['phase_hits'] if task_summary else 0} "
    f"task_type2={task_summary['type2'] if task_summary else 0} task_overflow={task_summary['overflow'] if task_summary else 0} "
    f"post_task_rows={len(post_task_rows)} post_task_keys={len(set((row['width'], row['origin'], row['field']) for row in post_task_rows))} "
    f"post_detail_controls={int(detail_controls)} post_detail_overflow={detail_overflow} post_histogram_overflow={sum(post_hist_overflows)} "
    f"writer_gpr_rows={sum(writer_counts.values())} writer_direct_rows={source_direct_rows} writer_direct_phase_keys={source_direct_keys} "
    f"writer_vi_join=phase_field_scope_only verdict={verdict}"
)
for phase, field, data_ptr, field_ptr, count, direct, unique in phase_source_summary:
    direct_text = ",".join(f"{key}:{value}" for key, value in sorted(direct.items())) or "-"
    lines.append(
        f"source_phase={phase[0]}:0x{phase[1]:06X} task_field={hex_value(field)} data_ptr={hex_value(data_ptr)} "
        f"data_ptr_plus_100={hex_value(field_ptr)} writer_gpr_rows={count} source_tuples={unique} direct={direct_text}"
    )
(out_dir / "summary.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
if verdict == "H-CoverageInvalid":
    raise SystemExit(5)
