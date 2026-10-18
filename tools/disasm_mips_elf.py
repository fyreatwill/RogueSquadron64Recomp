#!/usr/bin/env python3
"""Minimal big-endian MIPS (CPU, not RSP) disassembler for an ELF's loaded segments.
usage: disasm_mips_elf.py ELF START STOP   (no objdump / rabbitizer dependency)"""
import struct
import sys

elf = open(sys.argv[1], "rb").read()
lo, hi = int(sys.argv[2], 0), int(sys.argv[3], 0)
is64 = elf[4] == 2
if is64:
    phoff, = struct.unpack(">Q", elf[0x20:0x28])
    phes, phn = struct.unpack(">HH", elf[0x36:0x3A])
else:
    phoff, = struct.unpack(">I", elf[0x1C:0x20])
    phes, phn = struct.unpack(">HH", elf[0x2A:0x2E])


def seg_bytes(a, n):
    a32 = a & 0xFFFFFFFF
    for i in range(phn):
        p = phoff + i * phes
        if is64:
            t, fl, off, va, pa, fs, ms, al = struct.unpack(">IIQQQQQQ", elf[p:p + 56])
        else:
            t, off, va, pa, fs, ms, fl, al = struct.unpack(">IIIIIIII", elf[p:p + 32])
        if t == 1 and (va & 0xFFFFFFFF) <= a32 < (va & 0xFFFFFFFF) + fs:
            o = off + (a32 - (va & 0xFFFFFFFF))
            return elf[o:o + n]
    raise SystemExit("addr not in any PT_LOAD")


data = seg_bytes(lo, hi - lo)
SP = {0: "sll", 2: "srl", 3: "sra", 4: "sllv", 6: "srlv", 7: "srav", 8: "jr", 9: "jalr", 12: "syscall", 16: "mfhi",
      18: "mflo", 24: "mult", 25: "multu", 26: "div", 27: "divu", 32: "add", 33: "addu", 34: "sub", 35: "subu",
      36: "and", 37: "or", 38: "xor", 39: "nor", 42: "slt", 43: "sltu", 44: "dadd", 45: "daddu"}
SH = {0: "sll", 2: "srl", 3: "sra", 56: "dsll", 58: "dsrl", 59: "dsra"}
IM = {8: "addi", 9: "addiu", 10: "slti", 11: "sltiu", 12: "andi", 13: "ori", 14: "xori", 24: "daddi", 25: "daddiu"}
LS = {0x20: "lb", 0x21: "lh", 0x23: "lw", 0x24: "lbu", 0x25: "lhu", 0x27: "lwu", 0x28: "sb", 0x29: "sh",
      0x2B: "sw", 0x37: "ld", 0x3F: "sd", 0x31: "lwc1", 0x39: "swc1"}
BR = {4: "beq", 5: "bne", 6: "blez", 7: "bgtz", 20: "beql", 21: "bnel", 22: "blezl", 23: "bgtzl"}
for i in range(0, len(data), 4):
    w, = struct.unpack(">I", data[i:i + 4])
    pc = lo + i
    op, rs, rt, rd, sh, fn = w >> 26, (w >> 21) & 31, (w >> 16) & 31, (w >> 11) & 31, (w >> 6) & 31, w & 63
    imm = w & 0xFFFF
    simm = imm - 0x10000 if imm & 0x8000 else imm
    if w == 0:
        s = "nop"
    elif op == 0:
        if fn == 8:
            s = "jr r%d" % rs
        elif fn in SH:
            s = "%s r%d, r%d, %d" % (SH[fn], rd, rt, sh)
        else:
            s = "%s r%d, r%d, r%d" % (SP.get(fn, "sp?%d" % fn), rd, rs, rt)
    elif op == 1:
        s = "%s%s r%d, %08X" % ("bgez" if rt & 1 else "bltz", "l" if rt & 2 else "", rs, pc + 4 + simm * 4)
    elif op in (2, 3):
        s = "%s %08X" % ("jal" if op == 3 else "j", ((pc + 4) & 0xF0000000) | ((w & 0x3FFFFFF) << 2))
    elif op in BR:
        s = "%s r%d, r%d, %08X" % (BR[op], rs, rt, pc + 4 + simm * 4)
    elif op == 15:
        s = "lui r%d, 0x%04X" % (rt, imm)
    elif op in IM:
        s = "%s r%d, r%d, %s" % (IM[op], rt, rs, hex(imm) if op in (12, 13, 14) else simm)
    elif op in LS:
        s = "%s r%d, %d(r%d)" % (LS[op], rt, simm, rs)
    else:
        s = ".word 0x%08X" % w
    print("%08X: %08X  %s" % (pc, w, s))
