#!/usr/bin/env python3
"""Census of MIPS COP1 compare instructions whose condition includes the UNORDERED bit.
N64Recomp (src/operations.cpp:105-140) lowers c.un/ueq/ult/ule/ngle/ngl/nge/ngt to the same plain C
compare as the ordered forms (or constant false for un/ngle), so on a NaN operand they give 0 where
MIPS gives 1. This tool scans the ROM for COP1 S/D compares (opcode 0x11, fmt 16/17, funct 0x30-0x3F)
and reports per-condition counts, requiring a bc1t/bc1f within 3 words (code-shape filter vs data).
Usage: census_fcmp_unordered.py <rom.z64>"""
import struct, sys, collections
rom = open(sys.argv[1] if len(sys.argv) > 1 else "rs64.n64.us.1.0.z64", "rb").read()
n = len(rom) // 4
w = struct.unpack(">%dI" % n, rom[: n * 4])
names = "f un eq ueq olt ult ole ule sf ngle seq ngl lt nge le ngt".split()
tot = collections.Counter(); filt = collections.Counter(); examples = {}
for i, x in enumerate(w):
    if x >> 26 != 0x11 or ((x >> 21) & 0x1F) not in (16, 17) or (x & 0x3F) < 0x30:
        continue
    cond = x & 0xF
    key = (names[cond], "s" if (x >> 21) & 1 == 0 else "d")
    tot[key] += 1
    if any((w[j] >> 16) in (0x4501, 0x4500, 0x4503, 0x4502) for j in range(i + 1, min(i + 4, n))):
        filt[key] += 1; examples.setdefault(key, []).append(i * 4)
print("cond fmt total code-shaped unordered-bit")
for k in sorted(tot):
    c = [kk for kk in range(16) if names[kk] == k[0]][0]
    print(k[0], k[1], tot[k], filt[k], "UNORD" if c & 1 else "ordered")
bad = sum(v for k, v in filt.items() if [c for c in range(16) if names[c] == k[0]][0] & 1)
print("code-shaped sites with unordered bit:", bad, " (c.f/c.sf/c.un lowered to constant false: 'f','sf','un','ngle' included only if odd)")
for k, v in examples.items():
    if [c for c in range(16) if names[c] == k[0]][0] & 1:
        print(k, [hex(a) for a in v[:8]])
