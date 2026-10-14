#!/usr/bin/env python3
"""Audit generated 64-bit MIPS shifts against the independent retail ELF."""

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
SHIFT = re.compile(r"\b(dsll32|dsrl32|dsra32|dsllv|dsrlv|dsrav|dsll|dsrl|dsra)\s+\$([^,]+),\s*\$([^,]+)(?:,\s*([^\s#]+))?")
FUNCTS = {0x14: "dsllv", 0x16: "dsrlv", 0x17: "dsrav", 0x38: "dsll", 0x3A: "dsrl", 0x3B: "dsra", 0x3C: "dsll32", 0x3E: "dsrl32", 0x3F: "dsra32"}


def elf_words(path: Path):
    data = path.read_bytes()
    if data[:4] != b"\x7fELF" or data[4] != 1 or data[5] != 2:
        raise ValueError("expected a 32-bit big-endian ELF")
    hdr = struct.unpack_from(">16sHHIIIIIHHHHHH", data, 0)
    _, _, _, _, _, _, shoff, _, _, _, _, shentsize, shnum, _ = hdr
    words = {}
    for i in range(shnum):
        fields = struct.unpack_from(">IIIIIIIIII", data, shoff + i * shentsize)
        fileoff, size, addr = fields[4], fields[5], fields[3]
        if addr and size and fileoff:
            payload = data[fileoff:fileoff + size]
            for off in range(0, len(payload) - 3, 4):
                words[addr + off] = struct.unpack_from(">I", payload, off)[0]
    return words


def decode(word):
    if word is None or (word >> 26) != 0:
        return None
    name = FUNCTS.get(word & 0x3F)
    if not name:
        return None
    rd, rt, rs, shamt = (word >> 11) & 31, (word >> 16) & 31, (word >> 21) & 31, (word >> 6) & 31
    if name.endswith("v"):
        return name, REGS[rd], REGS[rt], REGS[rs], None
    return name, REGS[rd], REGS[rt], None, shamt


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
    dst, src = row["annotation"][1], row["annotation"][2]
    dst_expr = f"ctx->r{REGS.index(dst)}"
    src_expr = "0" if src == "zero" else f"ctx->r{REGS.index(src)}"
    op, _, _, var, amount = row["decoded"]
    if op.endswith("v"):
        expected = rf"{dst_expr}\s*=.*{src_expr}.*>>|{dst_expr}\s*=.*{src_expr}.*<<"
    else:
        expected = rf"{dst_expr}\s*=.*{src_expr}.*(?:<<|>>).*"
    shape = bool(re.search(expected, body))
    signed = op in ("dsra", "dsra32", "dsrav")
    signed_ok = (not signed) or "SIGNED(" in body or "int64_t" in body or "(int64_t)" in body
    if op.endswith("v"):
        count_ok = ("0" in body) if var == "zero" else (bool(re.search(rf"r{REGS.index(var)}", body)) if var else False)
    else:
        count_ok = str(amount) in body
        if op.endswith("32"):
            count_ok = count_ok and "32" in body
    return shape and signed_ok and count_ok


def sites(path: Path, words):
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
        sm = SHIFT.search(gm.group(2))
        if not sm:
            continue
        function_start, function_end = next(((start, end) for start, end in ranges if start <= i < end), (0, len(lines)))
        index, reachable = cfg_reachable(lines, function_start, function_end)
        pc, annotation = int(gm.group(1), 16), gm.group(2).strip()
        cursor = i + 1
        while cursor < len(lines) and not GUEST.search(lines[cursor]):
            cursor += 1
        body = " ".join(x.strip() for x in lines[i + 1:cursor] if x.strip())
        word = words.get(pc)
        decoded = decode(word)
        expected = (sm.group(1), sm.group(2).lower(), sm.group(3).lower(), sm.group(4).lstrip("$") if sm.group(4) else None)
        rows.append({"file": path.name, "line": i + 1, "function": function, "pc": pc, "annotation": expected, "text": annotation, "word": word, "decoded": decoded, "body": body, "lowered": False, "reachable": any(index.get(x) in reachable for x in range(i + 1, cursor) if x in index)})
        rows[-1]["lowered"] = lowering(rows[-1]) if decoded else False
    return rows


def classify(row):
    annotation = row["annotation"]
    if annotation[0].endswith("v"):
        expected = annotation[:3] + (annotation[3], None)
    else:
        expected = annotation[:3] + (None, int(annotation[3]))
    if row["decoded"] != expected:
        return "ELF/annotation mismatch"
    if row["lowered"]:
        return "correct"
    if row["reachable"] and row["annotation"][1] != "zero":
        return "unsupported/live"
    return "data-like/unreachable-or-zero"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--elf", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    words = elf_words(Path(args.elf))
    rows = []
    for path in sorted(Path(args.source).glob("funcs_*.c")):
        rows.extend(sites(path, words))
    rows.sort(key=lambda r: (r["file"], r["line"]))
    counts = Counter(classify(r) for r in rows)
    op_counts = Counter(r["annotation"][0] for r in rows)
    decoded_count = sum(r["decoded"] is not None for r in rows)
    lowered_count = sum(r["lowered"] for r in rows)
    reachable_count = sum(r["reachable"] for r in rows)
    reachable_nonzero = sum(r["reachable"] and r["annotation"][1] != "zero" for r in rows)
    control = next((r for r in rows if r["decoded"] and r["annotation"][1] != "zero"), None)
    if control and control["annotation"][0].endswith("v"):
        control_expected = control["annotation"][:3] + (control["annotation"][3], None)
    elif control:
        control_expected = control["annotation"][:3] + (None, int(control["annotation"][3]))
    else:
        control_expected = None
    control_pass = control is not None and control["decoded"] == control_expected and control["lowered"]
    with Path(args.output).open("w") as out:
        out.write("# M3 generated 64-bit shift census\n\n")
        out.write("Static census only. The retail ELF supplies the independent raw word; generated C supplies the lowering and conservative CFG reachability.\n\n")
        out.write(f"- annotation rows: **{len(rows)}**\n- classifications: " + ", ".join(f"`{k}`={v}" for k, v in sorted(counts.items())) + "\n")
        out.write(f"- unique file/guest-PC sites: **{len({(r['file'], r['pc']) for r in rows})}**; raw ELF decodes: **{decoded_count}/{len(rows)}**; generated lowerings present: **{lowered_count}/{len(rows)}**\n")
        out.write(f"- conservative CFG: **{reachable_count}** reachable rows, including **{reachable_nonzero}** reachable nonzero-destination rows\n")
        out.write("- opcode counts: " + ", ".join(f"`{k}`={v}" for k, v in sorted(op_counts.items())) + "\n")
        if control:
            out.write(f"- positive control: `{control['file']}:{control['line']}` PC `0x{control['pc']:08X}`, raw=`0x{control['word']:08X}`, decode=`{control['decoded']}`, lowering={'present' if control_pass else 'ABSENT'}; **{'PASS' if control_pass else 'FAIL'}**\n\n")
        out.write("## Interpretation\n\n")
        if counts["unsupported/live"]:
            out.write("A reachable nonzero-destination mismatch exists; the double-shift translation class is not closed.\n\n")
        elif counts["ELF/annotation mismatch"]:
            out.write("The raw ELF and generated annotations disagree at one or more sites; these require provenance review before class closure.\n\n")
        else:
            out.write("No reachable nonzero-destination mismatch was found. The class is statically closed as correct or data-like/unreachable; this does not claim qualified-route reachability.\n\n")
        out.write("## Complete site table\n\n| file:line | function | guest PC | raw word | ELF decode | annotation | lowering | CFG | classification |\n|---|---|---:|---:|---|---|---|---|---|\n")
        for r in rows:
            word = "—" if r["word"] is None else f"`0x{r['word']:08X}`"
            dec = "—" if r["decoded"] is None else " ".join(str(x) for x in r["decoded"])
            out.write(f"| {r['file']}:{r['line']} | `{r['function']}` | `0x{r['pc']:08X}` | {word} | `{dec}` | `{r['text']}` | {'yes' if r['lowered'] else 'NO'} | {'reachable' if r['reachable'] else 'unreachable'} | **{classify(r)}** |\n")


if __name__ == "__main__":
    main()
