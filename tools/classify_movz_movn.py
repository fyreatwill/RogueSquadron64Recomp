#!/usr/bin/env python3
"""Classify generated movz/movn sites using the containing C CFG."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

GUEST = re.compile(r"//\s+0x([0-9A-Fa-f]+):\s+(.*)")
FUNC = re.compile(r"RECOMP_FUNC\s+void\s+(\w+)\(")
MOV = re.compile(r"\b(movz|movn)\s+\$([^,]+),\s*\$([^,]+),\s*\$([^\s#]+)")
LABEL = re.compile(r"^\s*(L_[0-9A-Fa-f]+|skip_[0-9]+):")
GOTO = re.compile(r"\bgoto\s+(L_[0-9A-Fa-f]+|skip_[0-9]+)\s*;")


def executable(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and not stripped.startswith("//")


def classify_function(lines: list[str], line_offset: int = 0):
    statements = [i for i, line in enumerate(lines) if executable(line)]
    index = {line: n for n, line in enumerate(statements)}
    labels = {}
    for line in statements:
        match = LABEL.match(lines[line])
        if match:
            labels[match.group(1)] = index[line]

    edges = [[] for _ in statements]
    for n, line in enumerate(statements):
        text = lines[line]
        match = GOTO.search(text)
        if match and match.group(1) in labels:
            edges[n].append(labels[match.group(1)])
        if "return;" not in text and n + 1 < len(statements):
            # A generated goto can be inside an if body; retaining fall-through
            # is the conservative edge for this line-level analysis.
            edges[n].append(n + 1)
    reachable = set()
    if statements:
        pending = [0]
        while pending:
            node = pending.pop()
            if node in reachable:
                continue
            reachable.add(node)
            pending.extend(edges[node])

    guest_nodes = []
    label_targets = {}
    pending_labels = []
    for line_no, line in enumerate(lines):
        label = LABEL.match(line)
        if label:
            pending_labels.append(label.group(1))
        guest = GUEST.search(line)
        if guest:
            node = len(guest_nodes)
            guest_nodes.append((line_no, guest.group(2).strip()))
            for name in pending_labels:
                label_targets[name] = node
            pending_labels = []

    guest_edges = [[] for _ in guest_nodes]
    transfer = re.compile(r"\b(jr|jalr|j|beq|bne|bltz|bgez|blez|bgtz|bc[01][ft]l?)\b")
    for n, (_, text) in enumerate(guest_nodes):
        prior = guest_nodes[n - 1][1] if n else ""
        prior_match = transfer.search(prior)
        if prior_match:
            op = prior_match.group(1)
            target = re.search(r"\b(L_[0-9A-Fa-f]+)\b", prior)
            if target and target.group(1) in label_targets:
                guest_edges[n].append(label_targets[target.group(1)])
            if op.startswith(("b", "bc")) and n + 1 < len(guest_nodes):
                guest_edges[n].append(n + 1)
            continue
        if n + 1 >= len(guest_nodes):
            continue
        guest_edges[n].append(n + 1)

    guest_reachable = set()
    if guest_nodes:
        pending = [0]
        while pending:
            node = pending.pop()
            if node in guest_reachable:
                continue
            guest_reachable.add(node)
            pending.extend(guest_edges[node])
    guest_by_line = {line_no: n for n, (line_no, _) in enumerate(guest_nodes)}

    records = []
    function = "(preamble)"
    previous_guest = None
    for line_no, line in enumerate(lines):
        match = FUNC.search(line)
        if match:
            function = match.group(1)
        guest = GUEST.search(line)
        if not guest:
            continue
        move = MOV.search(guest.group(2))
        if not move:
            previous_guest = guest
            continue
        next_line = line_no + 1
        while next_line < len(lines) and not executable(lines[next_line]):
            next_line += 1
        node = index.get(next_line)
        guest_node = guest_by_line.get(line_no)
        before = []
        cursor = line_no - 1
        while cursor >= 0 and len(before) < 4:
            if executable(lines[cursor]):
                before.append(lines[cursor].strip())
            cursor -= 1
        text = guest.group(2).strip()
        records.append({
            "line": line_offset + line_no + 1,
            "function": function,
            "pc": int(guest.group(1), 16),
            "op": move.group(1),
            "dest": move.group(2).lower(),
            "raw": ".word" in text,
            "reachable": guest_node in guest_reachable,
            "before": before,
            "previous_guest": previous_guest.group(2).strip() if previous_guest else "(function entry)",
        })
        previous_guest = guest
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="../N64Recomp/RecompiledFuncs")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    source = Path(args.source)
    all_records = []
    for path in sorted(source.glob("funcs_*.c")):
        lines = path.read_text(errors="replace").splitlines()
        starts = [i for i, line in enumerate(lines) if FUNC.search(line)]
        for position, start in enumerate(starts):
            end = starts[position + 1] if position + 1 < len(starts) else len(lines)
            records = classify_function(lines[start:end], start)
            for record in records:
                record["file"] = path.name
            all_records.extend(records)

    grouped = {}
    for record in all_records:
        grouped.setdefault((record["file"], record["pc"]), []).append(record)

    rows = []
    for key, copies in sorted(grouped.items()):
        reachable = [r for r in copies if r["reachable"]]
        if reachable:
            classification = "reachable"
            evidence = "reachable guest predecessor; " + "; ".join(
                f"line {r['line']} after {r['previous_guest']}" for r in reachable[:2]
            )
        else:
            post_return = all(any("return;" == x or x.endswith("return;") for x in r["before"]) for r in copies)
            classification = "post-return/unreachable" if post_return else "data-like/unreachable"
            evidence = "; ".join(
                f"line {r['line']} predecessor {r['previous_guest']}" for r in copies[:3]
            )
        rows.append((key, copies, classification, evidence))

    counts = Counter(row[2] for row in rows)
    out = Path(args.output)
    with out.open("w") as stream:
        stream.write("# M3 `movz`/`movn` generated-C reachability classification\n\n")
        stream.write("## Method\n\n")
        stream.write(
            "The 149 unique file/guest-PC sites from the s4840 census were classified "
            "by a guest-instruction CFG over each containing generated function. The first "
            "instruction is the entry; ordinary fall-through and branch targets are followed, "
            "and `jr`/`jalr` retain only their delay slot with no statically known successor. "
            "Duplicate emitted copies are grouped by file and guest PC. This is a static "
            "generated-C result, not runtime reachability.\n\n"
        )
        stream.write("## Result\n\n")
        stream.write("| classification | sites |\n|---|---:|\n")
        for name in ("reachable", "post-return/unreachable", "data-like/unreachable"):
            stream.write(f"| {name} | {counts[name]} |\n")
        stream.write("\n")
        stream.write("## Site table\n\n")
        stream.write("| file | guest PC | op/dest | copies | classification | predecessor evidence |\n|---|---:|---|---:|---|---|\n")
        for (file_name, pc), copies, classification, evidence in rows:
            ops = ", ".join(f"{r['op']} ${r['dest']}" for r in copies[:4])
            if len(copies) > 4:
                ops += f" (+{len(copies)-4} copies)"
            stream.write(f"| {file_name} | `0x{pc:08X}` | {ops} | {len(copies)} | {classification} | {evidence} |\n")


if __name__ == "__main__":
    main()
