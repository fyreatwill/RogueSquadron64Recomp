#!/usr/bin/env python3
"""Classify generic do_break sites by conservative generated-C reachability."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

GUEST = re.compile(r"//\s+0x([0-9A-Fa-f]+):\s+(.*)")
FUNC = re.compile(r"RECOMP_FUNC\s+void\s+(\w+)\(")
BREAK = re.compile(r"\bdo_break\(")
LABEL = re.compile(r"^\s*(L_[0-9A-Fa-f]+|skip_[0-9]+):")
GOTO = re.compile(r"\bgoto\s+(L_[0-9A-Fa-f]+|skip_[0-9]+)\s*;")
WORD = re.compile(r"\.word\s+0x([0-9A-Fa-f]{8})")


def classify(lines):
    executable = [i for i, line in enumerate(lines) if line.strip() and not line.lstrip().startswith("//")]
    index = {line: n for n, line in enumerate(executable)}
    labels = {m.group(1): index[i] for i, line in enumerate(lines) if (m := LABEL.match(line)) and i in index}
    edges = [[] for _ in executable]
    for n, line_no in enumerate(executable):
        text = lines[line_no]
        if (m := GOTO.search(text)) and m.group(1) in labels:
            edges[n].append(labels[m.group(1)])
        if "return;" not in text and n + 1 < len(executable):
            edges[n].append(n + 1)
    reachable = set()
    pending = [0] if executable else []
    while pending:
        n = pending.pop()
        if n in reachable: continue
        reachable.add(n); pending.extend(edges[n])
    function = "(preamble)"
    rows = []
    for i, line in enumerate(lines):
        if (m := FUNC.search(line)): function = m.group(1)
        gm = GUEST.search(line)
        if not gm: continue
        cursor = i + 1
        while cursor < len(lines) and not GUEST.search(lines[cursor]): cursor += 1
        if cursor == i + 1: continue
        if not any(BREAK.search(lines[x]) for x in range(i + 1, cursor)): continue
        next_exec = next((x for x in range(i + 1, cursor) if x in index), None)
        annotation = gm.group(2).strip()
        raw = WORD.search(annotation)
        word = int(raw.group(1), 16) if raw else (0x0000000F if annotation == "sync" else None)
        selected = "sync" in annotation and word is not None and (word & 0x03FFF800) == 0
        rows.append({"file_line": i + 1, "function": function, "pc": int(gm.group(1), 16), "selected": selected, "reachable": next_exec is not None and index[next_exec] in reachable, "post_return": any(lines[x].strip() == "return;" or lines[x].strip().endswith("return;") for x in range(max(0, i - 5), i))})
    return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--source", required=True); ap.add_argument("--output", required=True)
    args = ap.parse_args(); rows = []
    for path in sorted(Path(args.source).glob("funcs_*.c")):
        lines = path.read_text(errors="replace").splitlines()
        starts = [i for i, line in enumerate(lines) if FUNC.search(line)]
        for n, start in enumerate(starts):
            end = starts[n + 1] if n + 1 < len(starts) else len(lines)
            for row in classify(lines[start:end]):
                row["file"] = path.name; rows.append(row)
    grouped = {}
    for row in rows: grouped.setdefault((row["file"], row["pc"]), []).append(row)
    result = []
    for key, copies in sorted(grouped.items()):
        if any(r["reachable"] for r in copies): cls = "reachable"
        elif all(r["post_return"] for r in copies): cls = "post-return/unreachable"
        else: cls = "data-like/unreachable"
        result.append((key, copies, cls))
    counts = Counter(cls for _, _, cls in result)
    selected = [(key, copies, cls) for key, copies, cls in result if any(r["selected"] for r in copies)]
    selected_counts = Counter(cls for _, _, cls in selected)
    with Path(args.output).open("w") as f:
        f.write("# M3 generic `do_break` reachability classification\n\n")
        f.write("Conservative line-level generated-C CFG: entry, fall-through, explicit gotos, and returns. "
                "This is not runtime reachability and does not justify a behavior change by itself.\n\n")
        f.write("| classification | unique sites |\n|---|---:|\n")
        for name in ("reachable", "post-return/unreachable", "data-like/unreachable"): f.write(f"| {name} | {counts[name]} |\n")
        f.write(f"\nSelected valid `sync` sites: **{len(selected)}** unique sites; reachable **{selected_counts['reachable']}**, post-return **{selected_counts['post-return/unreachable']}**, data-like **{selected_counts['data-like/unreachable']}**.\n\n")
        f.write("| selected sync file | guest PC | copies | classification |\n|---|---:|---:|---|\n")
        for (file_name, pc), copies, cls in selected: f.write(f"| {file_name} | `0x{pc:08X}` | {len(copies)} | {cls} |\n")
        f.write("\n| file | guest PC | copies | classification |\n|---|---:|---:|---|\n")
        for (file_name, pc), copies, cls in result: f.write(f"| {file_name} | `0x{pc:08X}` | {len(copies)} | {cls} |\n")


if __name__ == "__main__": main()
