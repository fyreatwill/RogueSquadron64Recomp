#!/usr/bin/env python3
"""Census generated do_break sites whose guest instruction is CPU code.

This is deliberately a static, no-behavior-change audit.  The ELF reader is
small because the retail input is a big-endian 32-bit MIPS ELF and pyelftools
is not a project dependency.
"""

from __future__ import annotations

import argparse
import glob
import re
import struct
from collections import Counter
from pathlib import Path

REGS = ("zero", "at", "v0", "v1", "a0", "a1", "a2", "a3", "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7", "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "t8", "t9", "k0", "k1", "gp", "sp", "fp", "ra")
GUEST = re.compile(r"//\s+0x([0-9A-Fa-f]+):\s+(.*)")
FUNC = re.compile(r"RECOMP_FUNC\s+void\s+(\w+)\(")
BREAK = re.compile(r"\bdo_break\((\d+)\)")
WORD = re.compile(r"\.word\s+0x([0-9A-Fa-f]{8})")


def elf_words(path: Path):
    data = path.read_bytes()
    if data[:4] != b"\x7fELF" or data[4] != 1 or data[5] != 2:
        raise ValueError("expected a 32-bit big-endian ELF")
    hdr = struct.unpack_from(">16sHHIIIIIHHHHHH", data, 0)
    _, _, _, _, _, _, shoff, _, _, _, _, shentsize, shnum, shstrndx = hdr
    sections = []
    for i in range(shnum):
        off = shoff + i * shentsize
        name, kind, flags, addr, fileoff, size, _, _, _, _ = struct.unpack_from(">IIIIIIIIII", data, off)
        sections.append((name, kind, flags, addr, fileoff, size))
    names = sections[shstrndx]
    blob = data[names[4]:names[4] + names[5]]
    result = {}
    for name, _, _, addr, fileoff, size in sections:
        end = blob.find(b"\0", name)
        section_name = blob[name:end].decode(errors="replace")
        if not (addr and size and fileoff):
            continue
        payload = data[fileoff:fileoff + size]
        for i in range(0, len(payload) - 3, 4):
            result[addr + i] = struct.unpack_from(">I", payload, i)[0]
    return result


def decode(word):
    op = word >> 26
    rs, rt, rd = (word >> 21) & 31, (word >> 16) & 31, (word >> 11) & 31
    funct = word & 0x3f
    if op == 0:
        names = {0x08: "jr", 0x09: "jalr", 0x0a: "movz", 0x0b: "movn", 0x0c: "syscall", 0x0d: "break", 0x0f: "sync", 0x10: "mfhi", 0x11: "mthi", 0x12: "mflo", 0x13: "mtlo", 0x18: "mult", 0x19: "multu", 0x1a: "div", 0x1b: "divu", 0x20: "add", 0x21: "addu", 0x22: "sub", 0x23: "subu", 0x24: "and", 0x25: "or", 0x26: "xor", 0x27: "nor", 0x2a: "slt", 0x2b: "sltu"}
        name = names.get(funct, f"special_0x{funct:02X}")
        if name == "sync" and word & 0x03FFF800:
            name = "special_0x0F"
        return f"{name} ${REGS[rd]},${REGS[rs]},${REGS[rt]}"
    names = {1: "regimm", 2: "j", 3: "jal", 4: "beq", 5: "bne", 6: "blez", 7: "bgtz", 8: "addi", 9: "addiu", 10: "slti", 11: "sltiu", 12: "andi", 13: "ori", 14: "xori", 15: "lui", 16: "cop0", 17: "cop1", 20: "beql", 21: "bnel", 22: "blezl", 23: "bgtzl", 32: "lb", 33: "lh", 34: "lwl", 35: "lw", 36: "lbu", 37: "lhu", 38: "lwr", 39: "lwu", 40: "sb", 41: "sh", 42: "swl", 43: "sw", 46: "swr", 55: "ld", 63: "sd"}
    return names.get(op, f"opcode_0x{op:02X}")


def parse(path: Path, words):
    lines = path.read_text(errors="replace").splitlines()
    function = "(preamble)"
    records = []
    for i, line in enumerate(lines):
        fm = FUNC.search(line)
        if fm:
            function = fm.group(1)
        gm = GUEST.search(line)
        if not gm:
            continue
        pc = int(gm.group(1), 16)
        cursor = i + 1
        body = []
        while cursor < len(lines) and not GUEST.search(lines[cursor]):
            body.append(lines[cursor])
            cursor += 1
        if not any(BREAK.search(x) for x in body):
            continue
        word = words.get(pc)
        annotation = gm.group(2).strip()
        records.append({"file": path.name, "line": i + 1, "function": function, "pc": pc, "word": word, "decoded": decode(word) if word is not None else None, "annotation": annotation, "body": " ".join(x.strip() for x in body if x.strip())})
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--elf", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    words = elf_words(Path(args.elf))
    records = []
    for name in sorted(glob.glob(str(Path(args.source) / "funcs_*.c"))):
        records.extend(parse(Path(name), words))
    decoded = [r for r in records if r["decoded"]]
    counts = Counter(r["decoded"].split()[0] for r in decoded)
    sync = [r for r in decoded if r["decoded"].startswith("sync ")]
    out = Path(args.output)
    with out.open("w") as f:
        f.write("# M3 generic `do_break` CPU-instruction census\n\n")
        f.write("This is a static census only; it changes no generated output or runtime behavior. "
                "Every row is a generated guest annotation followed by a `do_break`; the raw word "
                "comes independently from the retail ELF at that guest PC.\n\n")
        f.write(f"- generated `do_break` sites with ELF words: **{len(decoded)}** / {len(records)}\n")
        f.write(f"- unique file/guest-PC sites: **{len({(r['file'], r['pc']) for r in records})}**\n")
        f.write(f"- selected valid `sync` sites (funct 0x0F with reserved fields clear): **{len(sync)}**\n")
        f.write("- decoded opcode counts: " + ", ".join(f"`{k}`={v}" for k, v in sorted(counts.items())) + "\n\n")
        f.write("## Site table\n\n| file:line | function | guest PC | raw word | independent decode | annotation |\n|---|---|---:|---:|---|---|\n")
        for r in records:
            word = "—" if r["word"] is None else f"`0x{r['word']:08X}`"
            f.write(f"| {r['file']}:{r['line']} | `{r['function']}` | `0x{r['pc']:08X}` | {word} | `{r['decoded'] or 'no ELF word'}` | `{r['annotation']}` |\n")


if __name__ == "__main__":
    main()
