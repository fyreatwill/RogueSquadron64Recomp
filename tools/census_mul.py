#!/usr/bin/env python3
"""Census generated 32-bit MIPS multiplication against the retail ELF."""

from __future__ import annotations

import argparse
import re
import struct
from collections import Counter
from pathlib import Path

REGS = ("zero", "at", "v0", "v1", "a0", "a1", "a2", "a3", "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7", "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "t8", "t9", "k0", "k1", "gp", "sp", "fp", "ra")
GUEST = re.compile(r"//\s+0x([0-9A-Fa-f]+):\s+(.*)")
FUNC = re.compile(r"RECOMP_FUNC\s+void\s+(\w+)\(")
LABEL = re.compile(r"^\s*(L_[0-9A-Fa-f]+|skip_[0-9]+):")
GOTO = re.compile(r"\bgoto\s+(L_[0-9A-Fa-f]+|skip_[0-9]+)\s*;")
MUL = re.compile(r"\b(multu?)\s+\$([^,\s]+),\s*\$([^,\s]+)")
FUNCTS = {0x18: "mult", 0x19: "multu"}


def elf_words(path: Path):
    data = path.read_bytes()
    if data[:4] != b"\x7fELF" or data[4] != 1 or data[5] != 2:
        raise ValueError("expected a 32-bit big-endian ELF")
    header = struct.unpack_from(">16sHHIIIIIHHHHHH", data, 0)
    _, _, _, _, _, _, shoff, _, _, _, _, shentsize, shnum, _ = header
    words = {}
    for i in range(shnum):
        fields = struct.unpack_from(">IIIIIIIIII", data, shoff + i * shentsize)
        addr, fileoff, size = fields[3], fields[4], fields[5]
        if addr and size and fileoff:
            payload = data[fileoff:fileoff + size]
            for off in range(0, len(payload) - 3, 4):
                words[addr + off] = struct.unpack_from(">I", payload, off)[0]
    return words


def decode(word):
    if word is None or (word >> 26) != 0:
        return None
    name = FUNCTS.get(word & 0x3F)
    if name is None:
        return None
    rs, rt = (word >> 21) & 31, (word >> 16) & 31
    return name, REGS[rs], REGS[rt]


def cfg_reachable(lines, start, end):
    executable = [i for i in range(start, end) if lines[i].strip() and not lines[i].lstrip().startswith("//")]
    index = {line: n for n, line in enumerate(executable)}
    labels = {m.group(1): index[i] for i, line in enumerate(lines) if (m := LABEL.match(line)) and i in index}
    edges = [[] for _ in executable]
    for n, line_no in enumerate(executable):
        text = lines[line_no]
        if (m := GOTO.search(text)) and m.group(1) in labels:
            edges[n].append(labels[m.group(1)])
        if "return;" not in text and n + 1 < len(executable):
            edges[n].append(n + 1)
    seen, todo = set(), [0] if executable else []
    while todo:
        n = todo.pop()
        if n in seen:
            continue
        seen.add(n)
        todo.extend(edges[n])
    return index, seen


def lowering(row):
    body = row["body"]
    op, rs, rt = row["annotation"]
    signed = op == "mult"
    cast = r"S64\(S32\(" if signed else r"U64\(U32\("
    return bool(re.search(r"result\s*=\s*" + cast, body)) and "lo =" in body and "hi =" in body


def collect(path: Path, words):
    lines = path.read_text(errors="replace").splitlines()
    starts = [i for i, line in enumerate(lines) if FUNC.search(line)]
    ranges = [(start, starts[n + 1] if n + 1 < len(starts) else len(lines)) for n, start in enumerate(starts)]
    function = "(preamble)"
    rows = []
    for i, line in enumerate(lines):
        if m := FUNC.search(line):
            function = m.group(1)
        gm = GUEST.search(line)
        if not gm:
            continue
        mm = MUL.search(gm.group(2))
        if not mm:
            continue
        function_start, function_end = next((x for x in ranges if x[0] <= i < x[1]), (0, len(lines)))
        index, reachable = cfg_reachable(lines, function_start, function_end)
        cursor = i + 1
        while cursor < len(lines) and not GUEST.search(lines[cursor]):
            cursor += 1
        body = " ".join(x.strip() for x in lines[i + 1:cursor] if x.strip())
        pc = int(gm.group(1), 16)
        annotation = (mm.group(1), mm.group(2).lower(), mm.group(3).lower())
        word = words.get(pc)
        decoded = decode(word)
        rows.append({
            "file": path.name, "line": i + 1, "function": function, "pc": pc,
            "annotation": annotation, "text": gm.group(2).strip(), "word": word,
            "decoded": decoded, "body": body, "lowered": False,
            "reachable": any(index.get(x) in reachable for x in range(i + 1, cursor) if x in index),
        })
        rows[-1]["lowered"] = lowering(rows[-1]) if decoded else False
    return rows


def classify(row):
    if row["decoded"] != row["annotation"]:
        return "ELF/annotation mismatch"
    if row["lowered"]:
        return "correct"
    if row["reachable"]:
        return "unsupported/live"
    return "data-like/unreachable"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--elf", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    words = elf_words(Path(args.elf))
    rows = []
    for path in sorted(Path(args.source).glob("funcs_*.c")):
        rows.extend(collect(path, words))
    rows.sort(key=lambda r: (r["file"], r["line"]))
    counts = Counter(classify(r) for r in rows)
    decoded = sum(r["decoded"] is not None for r in rows)
    lowered = sum(r["lowered"] for r in rows)
    reachable = sum(r["reachable"] for r in rows)
    control = next((r for r in rows if r["decoded"] is not None), None)
    control_pass = control is not None and control["decoded"] == control["annotation"] and control["lowered"]
    with Path(args.output).open("w") as out:
        out.write("# M3 generated 32-bit multiplication census\n\n")
        out.write("Static census only. The retail ELF supplies the independent raw word; generated C supplies the signedness lowering and conservative CFG reachability. The generated tree contains `mult`/`multu` annotations, not integer `mul` annotations, so this is the applicable 32-bit multiplication class.\n\n")
        out.write(f"- annotation rows: **{len(rows)}**; unique file/guest-PC sites: **{len({(r['file'], r['pc']) for r in rows})}**\n")
        out.write(f"- raw ELF decodes: **{decoded}/{len(rows)}**; generated lowerings present: **{lowered}/{len(rows)}**; conservative CFG reachable: **{reachable}**\n")
        out.write("- classifications: " + ", ".join(f"`{k}`={v}" for k, v in sorted(counts.items())) + "\n")
        if control:
            out.write(f"- positive control: `{control['file']}:{control['line']}` PC `0x{control['pc']:08X}`, raw=`0x{control['word']:08X}`, decode=`{control['decoded']}`, lowering={'present' if control_pass else 'ABSENT'}; **{'PASS' if control_pass else 'FAIL'}**\n\n")
        out.write("## Interpretation\n\n")
        if counts["unsupported/live"]:
            out.write("A reachable multiplication annotation lacks the expected signedness/width lowering; the class is not closed.\n\n")
        elif counts["ELF/annotation mismatch"]:
            out.write("The raw ELF and generated annotations disagree at one or more sites; provenance review is required before closure.\n\n")
        else:
            out.write("No reachable multiplication mismatch was found; the class is statically correct or data-like/unreachable. This does not claim qualified-route reachability.\n\n")
        out.write("## Complete site table\n\n| file:line | function | guest PC | raw word | ELF decode | annotation | lowering | CFG | classification |\n|---|---|---:|---:|---|---|---|---|---|\n")
        for r in rows:
            word = "—" if r["word"] is None else f"`0x{r['word']:08X}`"
            dec = "—" if r["decoded"] is None else " ".join(r["decoded"])
            out.write(f"| {r['file']}:{r['line']} | `{r['function']}` | `0x{r['pc']:08X}` | {word} | `{dec}` | `{r['text']}` | {'yes' if r['lowered'] else 'NO'} | {'reachable' if r['reachable'] else 'unreachable'} | **{classify(r)}** |\n")


if __name__ == "__main__":
    main()
