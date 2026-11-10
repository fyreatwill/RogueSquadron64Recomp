#!/usr/bin/env python3
"""s7081: minimal big-endian MIPS III interpreter used as an independent
reference for the voice resampler block (0x8009264C..0x800934A4). It executes
the RETAIL bytes from the ELF's .entry+.text segment, so it shares nothing with
N64Recomp's output. Only the opcodes this block uses are implemented; anything
else raises, so an unsupported path cannot pass silently."""
import struct

M64 = (1 << 64) - 1
BASE = 0x80000000
SIZE = 0x800000


def sx32(v):
    v &= 0xFFFFFFFF
    return (v - (1 << 32) if v & 0x80000000 else v) & M64


def s64(v):
    v &= M64
    return v - (1 << 64) if v >> 63 else v


def s32(v):
    v &= 0xFFFFFFFF
    return v - (1 << 32) if v >> 31 else v


class Mem:
    def __init__(self):
        self.b = bytearray(SIZE)

    def off(self, a, n):
        a &= 0xFFFFFFFF
        o = a - BASE
        if o < 0 or o + n > SIZE or a % n:
            raise MemoryError(f"bad access 0x{a:08X} size {n}")
        return o

    def rd(self, a, n):
        o = self.off(a, n)
        return int.from_bytes(self.b[o:o + n], 'big')

    def wr(self, a, n, v):
        o = self.off(a, n)
        self.b[o:o + n] = (v & ((1 << (8 * n)) - 1)).to_bytes(n, 'big')


def load_segment(mem, elf_path):
    """Copy every PROGBITS section in KSEG0 main RAM (not overlays) into mem."""
    d = open(elf_path, 'rb').read()
    shoff, = struct.unpack('>I', d[0x20:0x24])
    shentsize, shnum, shstrndx = struct.unpack('>HHH', d[0x2E:0x34])
    secs = [struct.unpack('>IIIIIIIIII', d[shoff + i * shentsize: shoff + (i + 1) * shentsize]) for i in range(shnum)]
    strtab = secs[shstrndx]
    names = d[strtab[4]: strtab[4] + strtab[5]]
    loaded = []
    for s in secs:
        name = names[s[0]: names.index(b'\0', s[0])].decode()
        typ, addr, off, size = s[1], s[3], s[4], s[5]
        if typ == 1 and name in ('.entry', '.text', '.data', '.rodata') and BASE <= addr < BASE + SIZE:
            mem.b[addr - BASE: addr - BASE + size] = d[off: off + size]
            loaded.append((name, addr, size))
    return loaded


def run(mem, regs, pc, stop_pc, limit=2_000_000):
    r = [x & M64 for x in regs]
    hi = lo = 0
    steps = 0

    def exec1(ins, pc):
        """Execute one instruction; return branch target or None."""
        nonlocal hi, lo
        op = ins >> 26
        rs, rt, rd, sa, fn = (ins >> 21) & 31, (ins >> 16) & 31, (ins >> 11) & 31, (ins >> 6) & 31, ins & 63
        imm = ins & 0xFFFF
        simm = imm - 0x10000 if imm & 0x8000 else imm
        tgt = None

        def w(reg, v):
            if reg:
                r[reg] = v & M64
        if op == 0:
            if fn == 0x00: w(rd, sx32((r[rt] & 0xFFFFFFFF) << sa))
            elif fn == 0x02: w(rd, sx32((r[rt] & 0xFFFFFFFF) >> sa))
            elif fn == 0x03: w(rd, sx32(s32(r[rt]) >> sa))
            elif fn == 0x08: tgt = r[rs] & 0xFFFFFFFF
            elif fn == 0x10: w(rd, hi)
            elif fn == 0x12: w(rd, lo)
            elif fn == 0x18:
                p = s32(r[rs]) * s32(r[rt]); lo = sx32(p); hi = sx32(p >> 32)
            elif fn == 0x21: w(rd, sx32(r[rs] + r[rt]))
            elif fn == 0x23: w(rd, sx32(r[rs] - r[rt]))
            elif fn == 0x24: w(rd, r[rs] & r[rt])
            elif fn == 0x25: w(rd, r[rs] | r[rt])
            elif fn == 0x26: w(rd, r[rs] ^ r[rt])
            elif fn == 0x27: w(rd, ~(r[rs] | r[rt]))
            elif fn == 0x2A: w(rd, 1 if s64(r[rs]) < s64(r[rt]) else 0)
            elif fn == 0x2B: w(rd, 1 if r[rs] < r[rt] else 0)
            elif fn == 0x38: w(rd, r[rt] << sa)
            elif fn == 0x3A: w(rd, r[rt] >> sa)
            elif fn == 0x3B: w(rd, s64(r[rt]) >> sa)
            elif fn == 0x3C: w(rd, r[rt] << (sa + 32))
            elif fn == 0x3E: w(rd, r[rt] >> (sa + 32))
            elif fn == 0x3F: w(rd, s64(r[rt]) >> (sa + 32))
            else: raise NotImplementedError(f"SPECIAL fn 0x{fn:02X} at 0x{pc:08X}")
        elif op == 1:
            if rt == 0: tgt = (pc + 4 + (simm << 2)) & 0xFFFFFFFF if s64(r[rs]) < 0 else -1
            elif rt == 1: tgt = (pc + 4 + (simm << 2)) & 0xFFFFFFFF if s64(r[rs]) >= 0 else -1
            else: raise NotImplementedError(f"REGIMM rt {rt} at 0x{pc:08X}")
        elif op in (2, 3):
            if op == 3: w(31, sx32(pc + 8))
            tgt = ((pc + 4) & 0xF0000000) | ((ins & 0x3FFFFFF) << 2)
        elif op in (4, 5, 6, 7):
            a, b = s64(r[rs]), s64(r[rt])
            take = {4: a == b, 5: a != b, 6: a <= 0, 7: a > 0}[op]
            tgt = (pc + 4 + (simm << 2)) & 0xFFFFFFFF if take else -1
        elif op == 0x09: w(rt, sx32(r[rs] + simm))
        elif op == 0x0A: w(rt, 1 if s64(r[rs]) < simm else 0)
        elif op == 0x0B: w(rt, 1 if r[rs] < (simm & M64) else 0)
        elif op == 0x0C: w(rt, r[rs] & imm)
        elif op == 0x0D: w(rt, r[rs] | imm)
        elif op == 0x0E: w(rt, r[rs] ^ imm)
        elif op == 0x0F: w(rt, sx32(imm << 16))
        elif op == 0x2F: pass  # cache
        elif op in (0x20, 0x21, 0x23, 0x24, 0x25, 0x27, 0x37):
            a = (r[rs] + simm) & 0xFFFFFFFF
            n = {0x20: 1, 0x24: 1, 0x21: 2, 0x25: 2, 0x23: 4, 0x27: 4, 0x37: 8}[op]
            v = mem.rd(a, n)
            if op == 0x20: v = v - 256 if v & 0x80 else v
            elif op == 0x21: v = v - 65536 if v & 0x8000 else v
            elif op == 0x23: v = s32(v)
            w(rt, v)
        elif op in (0x28, 0x29, 0x2B, 0x3F):
            a = (r[rs] + simm) & 0xFFFFFFFF
            n = {0x28: 1, 0x29: 2, 0x2B: 4, 0x3F: 8}[op]
            mem.wr(a, n, r[rt])
        else:
            raise NotImplementedError(f"op 0x{op:02X} at 0x{pc:08X}")
        return tgt

    while pc != stop_pc:
        steps += 1
        if steps > limit:
            raise TimeoutError("instruction limit")
        ins = mem.rd(pc, 4)
        t = exec1(ins, pc)
        if t is None:
            pc += 4
            continue
        dins = mem.rd(pc + 4, 4)
        if (dins >> 26) in (2, 3, 4, 5, 6, 7) or ((dins >> 26) == 0 and (dins & 63) == 8):
            raise NotImplementedError("branch in delay slot")
        exec1(dins, pc + 4)
        pc = (pc + 8) if t == -1 else t
    return r, steps
