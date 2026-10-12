#!/usr/bin/env python3
"""Enumerate non-self zero-offset MEM_W loads in backward generated loops."""

from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
FILES = sorted(ROOT.glob("funcs_*.c"))
LOAD = re.compile(r"ctx->r(\d+)\s*=\s*MEM_W\(ctx->r(\d+),\s*0[xX]?0\s*\)")
FUNCTION = re.compile(r"\b(\w+)\(uint8_t\*\s*rdram,\s*recomp_context\*\s*ctx\)\s*\{")
LABEL = re.compile(r"^\s*(L_[0-9A-Fa-f]+):")
GOTO = re.compile(r"goto\s+(L_[0-9A-Fa-f]+)")
PC = re.compile(r"//\s+(0x[0-9A-Fa-f]+):")


def scan(path):
    lines = path.read_text(errors="replace").splitlines()
    labels, gotos, rows = {}, [], []
    current = None
    last_pc = ""
    for n, line in enumerate(lines):
        match = FUNCTION.search(line)
        if match:
            current = match.group(1)
        match = LABEL.match(line)
        if match:
            labels[match.group(1)] = n
        for match in GOTO.finditer(line):
            gotos.append((n, match.group(1)))
        match = PC.search(line)
        if match:
            last_pc = match.group(1)
        match = LOAD.search(line)
        if match and current:
            rows.append({
                "file": path.name, "line": n + 1, "function": current,
                "pc": last_pc, "src": int(match.group(2)),
                "dst": int(match.group(1)), "lines": lines,
            })
    for row in rows:
        n = row["line"] - 1
        edges = [(labels[target], i, target) for i, target in gotos
                 if target in labels and labels[target] < i and labels[target] <= n <= i]
        if edges:
            _, edge, target = max(edges)
            row["target"], row["backedge"] = target, edge + 1
        else:
            row["target"], row["backedge"] = "", ""
    return rows


def classify(row):
    lines = row["lines"]
    start = row["line"]
    window = " ".join(lines[start:start + 14])
    reg = rf"ctx->r{row['dst']}"
    if re.search(rf"MEM_[A-Z]+\([^,]*{reg}", window):
        return "pointer-transition-review"
    if re.search(rf"ADD32\([^)]*{reg}|{reg}[^\n]*(?:<<|>>|&|\|)", window):
        return "derived-scalar-review"
    return "scalar-field"


def main():
    rows = [row for path in FILES for row in scan(path)]
    broad = re.compile(r"ctx->r\d+\s*=\s*MEM_W\(ctx->r\d+,\s*0[xX]?0\s*\)")
    second = []
    for path in FILES:
        second.extend((path.name, line_no) for line_no, line in enumerate(
            path.read_text(errors="replace").splitlines(), 1) if broad.search(line))
    assert len(rows) == len(second), (len(rows), len(second))
    loops = [row for row in rows if row["target"]]
    nonself = [row for row in loops if row["dst"] != row["src"]]
    print(f"all_direct={len(rows)} direct_control={len(second)} backward_loop={len(loops)} nonself={len(nonself)}")
    print("file\tline\tfunction\tguest_pc\tsrc\tdst\tloop_target\tbackedge\tclassification\tconsumer")
    for row in nonself:
        lines = row["lines"]
        consumer = " | ".join(line.strip() for line in lines[row["line"]:row["line"] + 4] if line.strip())
        print("\t".join(map(str, (row["file"], row["line"], row["function"], row["pc"],
                                    f"r{row['src']}", f"r{row['dst']}", row["target"],
                                    row["backedge"], classify(row), consumer))))


if __name__ == "__main__":
    main()
