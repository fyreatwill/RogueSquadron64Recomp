#!/usr/bin/env python3
"""s4977: one-shot census of three remaining M3 idiom classes over RecompiledFuncs:
 (a) dmfc1/dmtc1/mfc1/mtc1 widths + emitted-C for the 64-bit forms
 (b) sltiu: immediate sign-extension (negative imm) and emitted-C
 (c) jr with a non-$ra register: how the emitted C dispatches (jump table vs indirect)
Prints counts and a sample of emitted C for each distinct shape."""
import re, glob, collections
D = "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/"
hdr = re.compile(r"\s*// (0x[0-9A-F]{8}): (\w+)\s*(.*)")
cnt = collections.Counter(); sample = {}; seen = set()
sltiu_imm = collections.Counter(); jr_regs = collections.Counter()
for f in sorted(glob.glob(D + "*.c")):
    L = open(f, errors="replace").read().split("\n")
    for i, l in enumerate(L):
        m = hdr.match(l)
        if not m: continue
        a, op, rest = m.groups()
        if a in seen: continue
        if op in ("mfc1", "dmfc1", "mtc1", "dmtc1", "sltiu", "jr"):
            seen.add(a)
            nxt = L[i + 1].strip() if i + 1 < len(L) else ""
            if op == "jr":
                r = rest.strip()
                if r == "$ra": continue
                jr_regs[r] += 1
                key = ("jr", re.sub(r"\w+_\w+|0x[0-9a-f]+", "X", nxt)[:60])
            elif op == "sltiu":
                mm = re.search(r"(-?\w+)$", rest.strip()); imm = mm.group(1) if mm else "?"
                neg = imm.startswith("-")
                sltiu_imm["neg" if neg else "pos"] += 1
                key = ("sltiu", "neg" if neg else "pos", re.sub(r"\$\w+|r\d+", "R", nxt)[:70])
            else:
                key = (op, re.sub(r"\$\w+|\b[rf]\d+\b", "R", nxt)[:70])
            cnt[key] += 1; sample.setdefault(key, (a, nxt))
for k, c in sorted(cnt.items(), key=lambda x: -x[1]):
    print(c, k, sample[k])
print("sltiu imm sign:", dict(sltiu_imm))
print("jr non-ra regs:", dict(jr_regs))
