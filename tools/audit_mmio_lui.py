#!/usr/bin/env python3
"""s5350: census of `lui` immediates that could form N64 hardware-register (MMIO) or
KSEG1 (uncached) addresses, and the memory ops that consume them.

A lui whose upper half is outside 0x8000-0x807F (RDRAM KSEG0), i.e. 0x8080-0xFFFF, is a
candidate. Class buckets: kseg1-rdram (0xA000-0xA07F), mmio (0xA3F0-0xA4FF, 0xA500-0xA7FF,
0xBxxx), rom/other. For each candidate we follow the register forward within the basic
block (WINDOW insns, stopping at a redefinition) and record the lw/sw/etc that use it.

Usage: audit_mmio_lui.py <elf> <out> | --selftest
"""
import re, subprocess, sys

WINDOW = 16
MEM = {"lb", "lbu", "lh", "lhu", "lw", "lwu", "ld", "lwc1", "ldc1", "sb", "sh", "sw", "sd", "swc1", "sdc1",
       "lwl", "lwr", "swl", "swr", "ll", "sc"}
CTRL = {"beq", "bne", "beql", "bnel", "blez", "bgtz", "bltz", "bgez", "blezl", "bgtzl", "bltzl", "bgezl",
        "bltzal", "bgezal", "jr", "jalr", "j", "jal", "bc1t", "bc1f", "bc1tl", "bc1fl"}


def parse(lines):
    ins = []
    for l in lines:
        m = re.match(r"\s*([0-9a-f]+):\s+[0-9a-f]{8}\s+(\S+)\s*(.*)", l)
        if m:
            ins.append((int(m.group(1), 16), m.group(2), m.group(3).split("#")[0].strip()))
    return ins


def bucket(hi):
    if 0xA000 <= hi <= 0xA07F:
        return "kseg1-rdram"
    if 0xA3F0 <= hi <= 0xA4FF or 0xA500 <= hi <= 0xA7FF:
        return "mmio-A"
    if 0xB000 <= hi <= 0xBFFF:
        return "mmio-B/rom"
    if 0x8080 <= hi <= 0x9FFF:
        return "kseg0-high"
    return "other"


def audit(ins):
    cands, uses = [], []
    for i, (a, op, ops) in enumerate(ins):
        m = re.match(r"(\$?\w+),(0x[0-9a-f]+|\d+)$", ops)
        if op != "lui" or not m:
            continue
        hi = int(m.group(2), 0) & 0xFFFF
        if 0x8000 <= hi <= 0x807F or hi < 0x8000:
            continue
        reg = m.group(1)
        b = bucket(hi)
        cands.append((a, b, hi))
        for j in range(i + 1, min(i + 1 + WINDOW, len(ins))):
            aj, opj, opsj = ins[j]
            if aj != ins[j - 1][0] + 4:
                break
            mm = re.match(r"(\$?\w+),(-?\w+)\((\$?\w+)\)", opsj)
            if opj in MEM and mm and mm.group(3) == reg:
                uses.append((a, b, hi, aj, opj, int(mm.group(2), 0)))
            d = re.match(r"(\$?\w+),", opsj)
            if d and d.group(1) == reg and opj not in MEM - {"lw", "lb", "lbu", "lh", "lhu", "lwu", "ld"} \
               and opj not in CTRL and not (opj.startswith("s") and opj in MEM):
                break
            if opj in CTRL and j + 1 < len(ins):
                continue
    return cands, uses


SYN = """\
 100:\t3c04a440\tlui\t$4,0xa440
 104:\t8c820010\tlw\t$2,16($4)
 108:\t3c058100\tlui\t$5,0x8100
 10c:\t3c06b000\tlui\t$6,0xb000
 110:\t3c0780ff\tlui\t$7,0x80ff
"""

if sys.argv[1] == "--selftest":
    c, u = audit(parse(SYN.replace("\t", "  ").splitlines()))
    assert {x[1] for x in c} == {"mmio-A", "kseg0-high", "mmio-B/rom"}, c
    assert len(u) == 1 and u[0][4] == "lw" and u[0][5] == 16, u
    print("selftest ok: 3 non-RDRAM lui flagged (mmio-A, kseg0-high, mmio-B/rom), 80ff ignored, 1 use")
    sys.exit(0)

dis = subprocess.run(["mips-linux-gnu-objdump", "-d", "-M", "no-aliases", sys.argv[1]],
                     capture_output=True, text=True).stdout.splitlines()
ins = parse(dis)
cands, uses = audit(ins)
from collections import Counter
ctl = Counter()  # positive control: the parser must see the ordinary RDRAM lui population
for _, op, ops in ins:
    m = re.match(r"(\$?\w+),(0x[0-9a-f]+|\d+)$", ops)
    if op == "lui" and m:
        hi = int(m.group(2), 0) & 0xFFFF
        ctl["rdram-80xx" if 0x8000 <= hi <= 0x807F else "low" if hi < 0x8000 else "candidate"] += 1
with open(sys.argv[2], "w") as f:
    f.write("insns=%d candidates=%d uses=%d control=%s\n" % (len(ins), len(cands), len(uses), dict(ctl)))
    for k, v in sorted(Counter(c[1] for c in cands).items()):
        f.write("bucket %s: %d lui\n" % (k, v))
    for k, v in sorted(Counter((u[1], u[2]) for u in uses).items()):
        f.write("use bucket=%s hi=0x%04x : %d\n" % (k[0], k[1], v))
    for c in cands:
        f.write("lui %08x %s 0x%04x\n" % c)
    for u in uses:
        f.write("use lui@%08x %s hi=0x%04x at %08x %s off=%d\n" % u)
print(open(sys.argv[2]).read().split("lui ")[0])
