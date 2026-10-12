#!/usr/bin/env python3
"""Enumerate non-self zero-offset MEM_BU loads in backward generated loops."""

from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
FILES = sorted(ROOT.glob("funcs_*.c"))
LOAD = re.compile(r"ctx->r(\d+)\s*=\s*MEM_BU\(ctx->r(\d+),\s*0[xX]?0\s*\)")
DIRECT_CONTROL = re.compile(r"ctx->r\d+\s*=\s*MEM_BU\(ctx->r\d+,\s*0[xX]?0\s*\)")
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
        m = FUNCTION.search(line)
        if m:
            current = m.group(1)
        m = LABEL.match(line)
        if m:
            labels[m.group(1)] = n
        for m in GOTO.finditer(line):
            gotos.append((n, m.group(1)))
        m = PC.search(line)
        if m:
            last_pc = m.group(1)
        m = LOAD.search(line)
        if m and current:
            rows.append({
                "file": path.name, "line": n + 1, "function": current,
                "pc": last_pc, "src": int(m.group(2)), "dst": int(m.group(1)),
                "lines": lines,
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
    window = " ".join(lines[start:start + 5])
    reg = rf"ctx->r{row['dst']}"
    if re.search(rf"MEM_[A-Z]+\([^,]*{reg}", window):
        return "pointer-transition-review"
    if re.search(rf"ADD32\([^)]*{reg}|{reg}[^\n]*(?:<<|>>|&|\|)", window):
        return "derived-scalar-review"
    return "scalar-field"


def main():
    rows = [r for p in FILES for r in scan(p)]
    direct_control = sum(len(DIRECT_CONTROL.findall(p.read_text(errors="replace"))) for p in FILES)
    assert len(rows) == direct_control, (len(rows), direct_control)
    loops = [r for r in rows if r["target"]]
    nonself = [r for r in loops if r["dst"] != r["src"]]
    print(f"all_direct={len(rows)} direct_control={direct_control} backward_loop={len(loops)} nonself={len(nonself)}")
    print("file\tline\tfunction\tguest_pc\tsrc\tdst\tloop_target\tbackedge\tclassification\tconsumer")
    for r in nonself:
        lines = r["lines"]
        consumer = " | ".join(x.strip() for x in lines[r["line"]:r["line"] + 4] if x.strip())
        print("\t".join(map(str, (r["file"], r["line"], r["function"], r["pc"],
                                    f"r{r['src']}", f"r{r['dst']}", r["target"],
                                    r["backedge"], classify(r), consumer))))


if __name__ == "__main__":
    main()
