#!/usr/bin/env python3
"""Audit generated translations of MIPS movz/movn instructions."""

import argparse
import re
from collections import Counter, defaultdict
from pathlib import Path

FUNC_RE = re.compile(r"^RECOMP_FUNC\s+.*?\b([A-Za-z0-9_]+)\s*\([^\n]*\)\s*\{", re.M)
MOV_RE = re.compile(r"\b(mov[zn])\s+\$(\w+),\s+\$(\w+),\s+\$(\w+)")
REGNUM = {
    "zero": 0, "at": 1, "v0": 2, "v1": 3, "a0": 4, "a1": 5,
    "a2": 6, "a3": 7, "t0": 8, "t1": 9, "t2": 10, "t3": 11,
    "t4": 12, "t5": 13, "t6": 14, "t7": 15, "s0": 16, "s1": 17,
    "s2": 18, "s3": 19, "s4": 20, "s5": 21, "s6": 22, "s7": 23,
    "t8": 24, "t9": 25, "k0": 26, "k1": 27, "gp": 28, "sp": 29,
    "fp": 30, "ra": 31,
}


def ctxreg(name):
    return f"ctx->r{REGNUM[name]}"


def classify_translation(lines, index, op, dst, src, cond):
    """Inspect the emitted C immediately following one guest instruction."""
    window = lines[index + 1:index + 9]
    if dst == "zero":
        return "zero-dest-discarded"
    expected_cond = ("0" if cond == "zero" else ctxreg(cond)) if op == "movn" else ("!0" if cond == "zero" else f"!{ctxreg(cond)}")
    expected_dst = ctxreg(dst)
    expected_src = "0" if src == "zero" else ctxreg(src)
    if_line = next((line.strip() for line in window if line.strip().startswith("if (")), None)
    assignment = next((line.strip() for line in window if re.search(r"ctx->r\d+\s*=", line)), None)
    if if_line is None or assignment is None:
        return "missing-translation"
    normalized = if_line.replace(" ", "").rstrip("{")
    wanted = f"if({expected_cond.replace(' ', '')})"
    if normalized != wanted:
        return "condition-mismatch"
    if not re.search(rf"{re.escape(expected_dst)}\s*=\s*{re.escape(expected_src)}\s*;", assignment):
        return "assignment-mismatch"
    return "exact"


def site_class(name, source_line):
    if (name.startswith(("data_gap_", "fake_func_")) or "$zero" in source_line.split("mov", 1)[-1].split(",", 1)[0]
            or ".word" in source_line or "InstrIdType" in source_line):
        return "invalid-or-data-gap"
    return "ordinary-generated"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="directory containing funcs_*.c")
    args = ap.parse_args()
    root = Path(args.root)
    paths = sorted(root.glob("funcs_*.c"))
    if not paths:
        raise SystemExit(f"no generated files under {root}")

    rows = []
    counts = Counter()
    for path in paths:
        text = path.read_text()
        functions = list(FUNC_RE.finditer(text))
        for fi, fn in enumerate(functions):
            end = functions[fi + 1].start() if fi + 1 < len(functions) else len(text)
            body = text[fn.start():end]
            lines = body.splitlines()
            base_line = text.count("\n", 0, fn.start()) + 1
            name = fn.group(1)
            for i, line in enumerate(lines):
                if not line.lstrip().startswith("//"):
                    continue
                match = MOV_RE.search(line)
                if not match:
                    continue
                op, dst, src, cond = match.groups()
                address = re.search(r"0x[0-9A-Fa-f]+", line)
                if not address:
                    continue
                translation = classify_translation(lines, i, op, dst, src, cond)
                row = {
                    "file": path.name,
                    "line": base_line + i,
                    "pc": address.group(0),
                    "function": name,
                    "op": op,
                    "dst": dst,
                    "src": src,
                    "cond": cond,
                    "translation": translation,
                    "site_class": site_class(name, line),
                }
                rows.append(row)
                counts.update((op, translation, row["site_class"]))

    unique = {}
    for row in rows:
        unique.setdefault((row["file"], row["pc"]), row)
    print(f"root={root}")
    print(f"files={len(paths)} functions={sum(len(list(FUNC_RE.finditer(p.read_text()))) for p in paths)} occurrences={len(rows)} unique_sites={len(unique)}")
    print("op_counts=" + ", ".join(f"{k}:{v}" for k, v in sorted((k, v) for k, v in counts.items() if k in {"movz", "movn"})))
    for key in ("exact", "zero-dest-discarded", "missing-translation", "condition-mismatch", "assignment-mismatch"):
        print(f"translation_{key}={sum(1 for r in rows if r['translation'] == key)}")
    print("site_class_counts=" + ", ".join(f"{k}:{v}" for k, v in sorted(Counter(r["site_class"] for r in unique.values()).items())))

    controls = {"ordinary": ("funcs_27.c", "0x800A3914"), "invalid": ("funcs_27.c", "0x8009F020")}
    for label, key in controls.items():
        matches = [r for r in rows if (r["file"], r["pc"]) == key]
        if not matches:
            raise SystemExit(f"positive control missing: {label} {key}")
        print(f"control_{label}=" + ";".join(f"{r['function']}:{r['op']} {r['dst']},{r['src']},{r['cond']} => {r['translation']} [{r['site_class']}]" for r in matches))
    ordinary = [r for r in rows if r["translation"] == "exact" and r["dst"] != "zero"]
    if not ordinary:
        raise SystemExit("positive control failed: no exact non-zero-destination translation")
    bad = [r for r in unique.values() if r["translation"] in {"condition-mismatch", "assignment-mismatch"} and r["site_class"] == "ordinary-generated"]
    for r in bad:
        print("MISMATCH", r)
    if bad:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
