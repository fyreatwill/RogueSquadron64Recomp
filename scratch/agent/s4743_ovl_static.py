#!/usr/bin/env python3
"""Static scan of a resident RSP overlay image: branch/jump targets, externals,
DMEM-relative scalar/vector memory ops. usage: s4743_ovl_static.py ROM_OFF LEN [DEST]"""
import struct, sys

rom = open("rs64.n64.us.1.0.z64", "rb").read()
off, ln = int(sys.argv[1], 0), int(sys.argv[2], 0)
dest = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x1DB0
img = rom[off:off + ln]
lo, hi = dest, dest + ln

SC = {0x23: "lw", 0x2B: "sw", 0x21: "lh", 0x25: "lhu", 0x20: "lb", 0x24: "lbu", 0x29: "sh", 0x28: "sb"}
VL = {0: "lbv", 1: "lsv", 2: "llv", 3: "ldv", 4: "lqv", 5: "lrv", 6: "lpv", 7: "luv", 8: "lhv", 9: "lfv", 11: "ltv"}
VS = {0: "sbv", 1: "ssv", 2: "slv", 3: "sdv", 4: "sqv", 5: "srv", 6: "spv", 7: "suv", 8: "shv", 9: "sfv", 10: "swv", 11: "stv"}
SCALE = {0: 1, 1: 2, 2: 4, 3: 8, 4: 16, 5: 16, 6: 8, 7: 8, 8: 16, 9: 16, 10: 16, 11: 16}

ext, inside, rows = set(), set(), []
for i in range(0, ln - 3, 4):
    pc = dest + i
    w = struct.unpack(">I", img[i:i + 4])[0]
    op, rs, rt, imm = w >> 26, (w >> 21) & 31, (w >> 16) & 31, w & 0xFFFF
    s = imm - 0x10000 if imm & 0x8000 else imm
    t = None
    txt = "%08x" % w
    if op in (1, 4, 5, 6, 7):
        t = ((pc + 4 + (s << 2)) & 0xFFF) | (pc & ~0xFFF)
        txt = "branch-op%d rs=%d rt=%d -> %#x" % (op, rs, rt, t)
    elif op in (2, 3):
        t = (((w & 0x3FFFFFF) << 2) & 0xFFF) | (pc & ~0xFFF)
        txt = "%s %#x" % ("jal" if op == 3 else "j", t)
    elif op == 0 and (w & 0x3F) in (8, 9):
        txt = "%s $%d (indirect)" % ("jr" if (w & 0x3F) == 8 else "jalr", rs)
    elif op in SC:
        txt = "%s $%d, %#x($%d)" % (SC[op], rt, s, rs)
    elif op in (0x32, 0x3A):
        sub = (w >> 11) & 31
        o7 = w & 0x7F
        o7 = o7 - 128 if o7 & 64 else o7
        name = (VL if op == 0x32 else VS).get(sub, "v?")
        txt = "%s vt=%d el=%d off=%d ($%d)" % (name, rt, (w >> 7) & 15, o7 * SCALE.get(sub, 1), rs)
    elif op == 0x12:
        txt = "cop2 %08x" % w
    rows.append((pc, txt))
    if t is not None:
        (inside if lo <= t < hi else ext).add(t)

print("image rom=%#x len=%#x dest=%#x..%#x" % (off, ln, lo, hi))
print("targets inside image:", sorted(hex(x) for x in inside))
print("EXTERNAL targets:", sorted(hex(x) for x in ext))
print("indirect jumps at:", [hex(p) for p, t in rows if "indirect" in t])
mem = [(p, t) for p, t in rows if t.split()[0] in SC.values()]
print("scalar mem ops:", len(mem))
for p, t in mem:
    print("  %#x %s" % (p, t))
vm = [(p, t) for p, t in rows if t.split()[0] in list(VL.values()) + list(VS.values())]
cop2 = sum(1 for p, t in rows if t.startswith("cop2"))
print("cop2 ops=%d vector ld/st=%d total insns=%d" % (cop2, len(vm), len(rows)))
print("--- control flow ---")
for p, t in rows:
    if "->" in t or t.startswith(("j ", "jal", "jr", "jalr")):
        print("%#x  %s" % (p, t))
print("--- vector ld/st ---")
for p, t in vm:
    print("%#x  %s" % (p, t))
