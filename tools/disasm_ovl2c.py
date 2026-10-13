#!/usr/bin/env python3
"""Self-contained RSP disassembly (no rabbitizer) of a resident Factor5 overlay image.
Default = overlay 0x2C (TexrectGen, DL op 0xBD). usage: disasm_ovl2c.py [ROM_OFF LEN DEST] (repo root)"""
import sys

rom = open("rs64.n64.us.1.0.z64", "rb").read()
off = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0x27368
ln = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x240
dest = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x1DB0


def R(n):
    return "$%d" % n


SP = {0: "sll", 2: "srl", 3: "sra", 4: "sllv", 6: "srlv", 7: "srav", 8: "jr", 9: "jalr", 13: "break",
      32: "add", 33: "addu", 34: "sub", 35: "subu", 36: "and", 37: "or", 38: "xor", 39: "nor", 42: "slt", 43: "sltu"}
IM = {8: "addi", 9: "addiu", 10: "slti", 11: "sltiu", 12: "andi", 13: "ori", 14: "xori", 15: "lui"}
LS = {0x20: "lb", 0x21: "lh", 0x23: "lw", 0x24: "lbu", 0x25: "lhu", 0x28: "sb", 0x29: "sh", 0x2B: "sw"}
VL = {0: "lbv", 1: "lsv", 2: "llv", 3: "ldv", 4: "lqv", 5: "lrv", 6: "lpv", 7: "luv", 8: "lhv", 9: "lfv", 11: "ltv"}
VS = {0: "sbv", 1: "ssv", 2: "slv", 3: "sdv", 4: "sqv", 5: "srv", 6: "spv", 7: "suv", 8: "shv", 9: "sfv", 10: "swv", 11: "stv"}
SC = {0: 1, 1: 2, 2: 4, 3: 8, 4: 16, 5: 16, 6: 8, 7: 8, 8: 16, 9: 16, 10: 16, 11: 16}
VO = {0: "vmulf", 1: "vmulu", 4: "vmudl", 5: "vmudm", 6: "vmudn", 7: "vmudh", 8: "vmacf", 9: "vmacu", 12: "vmadl",
      13: "vmadm", 14: "vmadn", 15: "vmadh", 16: "vadd", 17: "vsub", 19: "vabs", 20: "vaddc", 21: "vsubc", 29: "vsar",
      32: "vlt", 33: "veq", 34: "vne", 35: "vge", 36: "vcl", 37: "vch", 38: "vcr", 39: "vmrg", 40: "vand",
      41: "vnand", 42: "vor", 43: "vnor", 44: "vxor", 45: "vnxor", 48: "vrcp", 49: "vrcpl", 50: "vrcph",
      51: "vmov", 52: "vrsq", 53: "vrsql", 54: "vrsqh", 55: "vnop"}
REGIMM = {0: "bltz", 1: "bgez", 16: "bltzal", 17: "bgezal"}

for i in range(0, ln, 4):
    pc = dest + i
    w = int.from_bytes(rom[off + i:off + i + 4], "big")
    op, rs, rt, rd, sa, fn = w >> 26, (w >> 21) & 31, (w >> 16) & 31, (w >> 11) & 31, (w >> 6) & 31, w & 63
    imm = w & 0xFFFF
    s = imm - 0x10000 if imm & 0x8000 else imm
    bt = 0x1000 | ((pc + 4 + (s << 2)) & 0xFFF)
    if w == 0:
        t = "nop"
    elif op == 0:
        n = SP.get(fn, "special%d" % fn)
        if fn == 8:
            t = "jr %s" % R(rs)
        elif fn == 13:
            t = "break"
        elif fn in (0, 2, 3):
            t = "%s %s, %s, %d" % (n, R(rd), R(rt), sa)
        else:
            t = "%s %s, %s, %s" % (n, R(rd), R(rs), R(rt))
    elif op in (2, 3):
        t = "%s %#x" % ("j" if op == 2 else "jal", 0x1000 | (((w & 0x3FFFFFF) << 2) & 0xFFF))
    elif op in (4, 5):
        t = "%s %s, %s, %#x" % ("beq" if op == 4 else "bne", R(rs), R(rt), bt)
    elif op in (6, 7):
        t = "%s %s, %#x" % ("blez" if op == 6 else "bgtz", R(rs), bt)
    elif op == 1:
        t = "%s %s, %#x" % (REGIMM.get(rt, "regimm%d" % rt), R(rs), bt)
    elif op in IM:
        t = ("lui %s, %#x" % (R(rt), imm)) if op == 15 else "%s %s, %s, %d" % (IM[op], R(rt), R(rs), s)
    elif op in LS:
        t = "%s %s, %d(%s)" % (LS[op], R(rt), s, R(rs))
    elif op in (0x32, 0x3A):
        sub = (w >> 11) & 31
        o7 = w & 0x7F
        o7 = o7 - 128 if o7 & 64 else o7
        t = "%s v%d[%d], %d(%s)" % ((VL if op == 0x32 else VS).get(sub, "v?%d" % sub), rt, (w >> 7) & 15,
                                    o7 * SC.get(sub, 1), R(rs))
    elif op == 0x12:
        if w & 0x02000000:
            t = "%s v%d, v%d, v%d[e=%d]" % (VO.get(fn, "vop%d" % fn), sa, rd, rt, (w >> 21) & 15)
        else:
            sub = (w >> 21) & 31
            if sub in (0, 4):
                t = "%s %s, v%d[%d]" % ("mfc2" if sub == 0 else "mtc2", R(rt), rd, (w >> 7) & 15)
            elif sub in (2, 6):
                t = "%s %s, c%d" % ("cfc2" if sub == 2 else "ctc2", R(rt), rd)
            else:
                t = "cop2sub%d" % sub
    else:
        t = ".word %08x" % w
    print("%04x: %08x  %s" % (pc, w, t))
