#!/usr/bin/env python3
"""Audit generated HI/LO moves against the independent retail ELF."""

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
OPS = {0x10: "mfhi", 0x11: "mthi", 0x12: "mflo", 0x13: "mtlo"}


def elf_words(path: Path):
    data = path.read_bytes()
    if data[:4] != b"\x7fELF" or data[4] != 1 or data[5] != 2:
        raise ValueError("expected a 32-bit big-endian ELF")
    hdr = struct.unpack_from(">16sHHIIIIIHHHHHH", data, 0)
    _, _, _, _, _, _, shoff, _, _, _, _, shentsize, shnum, shstrndx = hdr
    sections = []
    for i in range(shnum):
        fields = struct.unpack_from(">IIIIIIIIII", data, shoff + i * shentsize)
        sections.append((fields[0], fields[4], fields[5], fields[3]))
    words = {}
    for _, fileoff, size, addr in sections:
        if addr and size and fileoff:
            payload = data[fileoff:fileoff + size]
            for i in range(0, len(payload) - 3, 4):
                words[addr + i] = struct.unpack_from(">I", payload, i)[0]
    return words


def decode(word):
    if word is None or (word >> 26) != 0 or (word & 0x3F) not in OPS:
        return None
    op = OPS[word & 0x3F]
    rs, rd = (word >> 21) & 31, (word >> 11) & 31
    reg = rd if op in ("mfhi", "mflo") else rs
    return op, REGS[reg], reg


def cfg_reachable(lines):
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
    seen, todo = set(), [0] if executable else []
    while todo:
        n = todo.pop()
        if n in seen:
            continue
        seen.add(n); todo.extend(edges[n])
    return index, seen


def sites(path: Path, words):
    lines = path.read_text(errors="replace").splitlines()
    index, reachable = cfg_reachable(lines)
    function = "(preamble)"
    rows = []
    for i, line in enumerate(lines):
        if m := FUNC.search(line):
            function = m.group(1)
        gm = GUEST.search(line)
        if not gm:
            continue
        annotation = gm.group(2).strip()
        named = re.search(r"\b(mfhi|mflo|mthi|mtlo)\s+\$(\w+)", annotation)
        if not named:
            continue
        pc = int(gm.group(1), 16)
        cursor = i + 1
        while cursor < len(lines) and not GUEST.search(lines[cursor]):
            cursor += 1
        body = " ".join(x.strip() for x in lines[i + 1:cursor] if x.strip())
        word = words.get(pc)
        decoded = decode(word)
        expected = (named.group(1), named.group(2), REGS.index(named.group(2)))
        next_exec = next((x for x in range(i + 1, cursor) if x in index), None)
        rows.append({"file": path.name, "line": i + 1, "function": function,
                     "pc": pc, "annotation": annotation, "word": word,
                     "decoded": decoded, "expected": expected, "body": body,
                     "reachable": next_exec is not None and index[next_exec] in reachable,
                     "lowered": (f"ctx->r{expected[2]} = {expected[0][2:]}" in body if expected[0] in ("mfhi", "mflo") else f"{expected[0][2:]} =" in body)} )
    return rows


def classify(row):
    if row["decoded"] != row["expected"]:
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
    rows = []
    for path in sorted(Path(args.source).glob("funcs_*.c")):
        rows.extend(sites(path, elf_words(Path(args.elf))))
    counts = Counter(classify(r) for r in rows)
    control = next((r for r in rows if r["pc"] == 0x80003444), None)
    with Path(args.output).open("w") as out:
        out.write("# M3 HI/LO move census\n\n")
        out.write("Static census only. The retail ELF supplies the independent raw word; generated C supplies the lowering and conservative CFG reachability.\n\n")
        out.write(f"- annotation rows: **{len(rows)}**\n- classifications: " + ", ".join(f"`{k}`={v}" for k, v in sorted(counts.items())) + "\n")
        if control:
            out.write(f"- positive control `0x80003444`: raw=`0x{control['word']:08X}`, decode=`{control['decoded'][0]} ${control['decoded'][1]}`, lowering={'present' if control['lowered'] else 'ABSENT'}\n\n")
        out.write("## Site table\n\n| file:line | function | guest PC | raw word | ELF decode | annotation | lowering | CFG | classification |\n|---|---|---:|---:|---|---|---|---|---|\n")
        for r in rows:
            word = "—" if r["word"] is None else f"`0x{r['word']:08X}`"
            dec = "—" if r["decoded"] is None else f"{r['decoded'][0]} ${r['decoded'][1]}"
            out.write(f"| {r['file']}:{r['line']} | `{r['function']}` | `0x{r['pc']:08X}` | {word} | `{dec}` | `{r['annotation']}` | {'yes' if r['lowered'] else 'NO'} | {'reachable' if r['reachable'] else 'unreachable'} | **{classify(r)}** |\n")


if __name__ == "__main__":
    main()
