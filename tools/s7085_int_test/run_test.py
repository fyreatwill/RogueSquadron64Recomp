#!/usr/bin/env python3
"""s7085: compile int_test.c with the live RecompiledFuncs flags (-O2, recomp.h from lib/), run it, and
compare every row against an exact R4300 (VR4300, 64-bit mode) integer reference:
  mult/multu/div/divu: 32-bit operands, lo/hi sign-extended; div INT_MIN/-1 -> lo=INT_MIN, hi=0.
  dmult/dmultu: 128-bit product. ddiv/ddivu: divisor 0 -> lo = (ddiv: a<0 ? 1 : -1; ddivu: -1), hi = a;
  ddiv INT64_MIN/-1 -> lo = a, hi = 0 (hardware results; C leaves these UB).
  sll/srl/sllv/srlv: 32-bit result sign-extended; sra/srav defined only for sign-extended inputs.
  dsll/dsrl/dsra 0..63. sltiu: unsigned compare against the SIGN-extended immediate.
  lwl/lwr/swl/swr: big-endian byte merge at every misalignment; a single partial lwr leaves bits
  63..32 implementation-defined, so only bits 31..0 are compared there.
  div guard (generated 0x800464F4 shape, variable divisor): do_break must still fire for /0 and INT_MIN/-1.
Negative control: the same rows against a reference that ZERO-extends 32-bit results must mismatch.
Exit 0 iff the real reference matches every row (before the s7085 recomp.h fix the 34 divisor-0
ddiv/ddivu rows failed: host lo=0) and the negative control mismatches > 0."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'scratch', 's7085')
M64 = (1 << 64) - 1

def build():
    os.makedirs(OUT, exist_ok=True)
    exe = os.path.join(OUT, 'int_test')
    inc = [os.path.join(ROOT, p) for p in ('include', 'lib/N64ModernRuntime/ultramodern/include',
           'lib/N64ModernRuntime/librecomp/include', 'lib/N64ModernRuntime/N64Recomp/include')]
    cmd = ['cc', '-g', '-std=gnu17', '-arch', 'arm64', '-O2', '-fno-strict-aliasing', '-w'] + \
          sum((['-I', i] for i in inc), []) + [os.path.join(HERE, 'int_test.c'), '-o', exe]
    subprocess.check_call(cmd)
    return exe

def s32(x): x &= 0xFFFFFFFF; return x - (1 << 32) if x & 0x80000000 else x
def s64(x): x &= M64; return x - (1 << 64) if x >> 63 else x
SEXT = True
def x32(v):  # 32-bit result into a 64-bit register
    return (s32(v) & M64) if SEXT else (v & 0xFFFFFFFF)
def is_sext(a): return s64(a) == s32(a)
def tdiv(a, b):
    q = abs(a) // abs(b); q = q if (a >= 0) == (b >= 0) else -q
    return q, a - q * b

def ref_muldiv(op, a, b):
    if op == 'mult': p = s32(a) * s32(b); return x32(p), x32(p >> 32)
    if op == 'multu': p = (a & 0xFFFFFFFF) * (b & 0xFFFFFFFF); return x32(p), x32(p >> 32)
    if op == 'div':
        if s32(a) == -2**31 and s32(b) == -1: return x32(a), 0
        q, r = tdiv(s32(a), s32(b)); return x32(q), x32(r)
    if op == 'divu': q, r = divmod(a & 0xFFFFFFFF, b & 0xFFFFFFFF); return x32(q), x32(r)
    if op == 'dmult': p = s64(a) * s64(b); return p & M64, (p >> 64) & M64
    if op == 'dmultu': p = a * b; return p & M64, (p >> 64) & M64
    if op == 'ddivu':
        if b == 0: return M64, a
        return a // b, a % b
    if op == 'ddiv':
        if b == 0: return (1 if s64(a) < 0 else M64), a
        if a == 1 << 63 and b == M64: return a, 0
        q, r = tdiv(s64(a), s64(b)); return q & M64, r & M64

def ref_shift(a, s):
    out = [x32(a << s) if s < 32 else 0, x32((a & 0xFFFFFFFF) >> s) if s < 32 else 0,
           x32(s32(a) >> s) if s < 32 else 0, x32(a << (s & 31)), x32((a & 0xFFFFFFFF) >> (s & 31)),
           x32(s32(a) >> (s & 31)), (a << s) & M64, a >> s, (s64(a) >> s) & M64]
    return out

def mem_bytes():
    return [(0x80 + b * 0x11) & 0xFF for b in range(16)]

def ref_lw(off, init):
    mem = mem_bytes(); r = 0x0123456789ABCDEF if init else 0
    word = int.from_bytes(bytes(mem[0:4]), 'big'); m = off
    def lwl(reg): v = ((word << (8 * m)) | (reg & ((1 << (8 * m)) - 1))) & 0xFFFFFFFF; return x32(v)
    def lwr(reg, mm):
        sh = 8 * (3 - mm); v = ((word >> sh) | (reg & ~(0xFFFFFFFF >> sh))) & 0xFFFFFFFF; return x32(v), mm == 3
    mid = lwl(r)
    full = int.from_bytes(bytes(mem[off:off + 4]), 'big')
    # pair lwl A ; lwr A+3 -> the 4 bytes at A, sign-extended
    w2 = int.from_bytes(bytes(mem[(off + 3) & ~3:((off + 3) & ~3) + 4]), 'big')
    sh = 8 * (3 - ((off + 3) & 3)); pair = x32(((w2 >> sh) | (mid & ~(0xFFFFFFFF >> sh))) & 0xFFFFFFFF)
    assert (pair & 0xFFFFFFFF) == full
    l3 = lwl(0x0123456789ABCDEF); l7, full7 = lwr(0x0123456789ABCDEF, m)
    return mid, pair, l3, l7, full7

def ref_sw(off, kind):
    val = 0xCAFEBABE.to_bytes(4, 'big')
    if kind == 'pair':
        mem = [0] * 8; mem[off:off + 4] = list(val); return mem
    mem = [0x55] * 8
    if kind == 'swl':
        for i in range(4 - off): mem[off + i] = val[i]
    else:
        for i in range(off + 1): mem[i] = val[3 - off + i]
    return mem

def check(lines):
    bad = []; rows = 0
    for ln in lines:
        t = ln.split(); op = t[0]; rows += 1
        if op in ('mult', 'multu', 'div', 'divu', 'dmult', 'dmultu', 'ddivu', 'ddiv'):
            a, b, lo, hi = (int(x, 16) for x in t[1:5])
            if (lo, hi) != ref_muldiv(op, a, b): bad.append((ln, ref_muldiv(op, a, b)))
        elif op == 'shift':
            a = int(t[1], 16); s = int(t[2]); got = [int(x, 16) for x in t[3:]]
            exp = ref_shift(a, s)
            for k in range(9):
                if k in (2, 5) and not is_sext(a): continue  # sra/srav undefined on non-sext input
                if got[k] != exp[k]: bad.append((ln, f'col{k} exp {exp[k]:x}'))
        elif op == 'imm':
            a = int(t[1], 16); imm = int(t[2]); u, sg, add = int(t[3]), int(t[4]), int(t[5], 16)
            other, sb = int(t[6], 16), int(t[7], 16)
            exp = (1 if a < (imm & M64) else 0, 1 if s64(a) < imm else 0, x32(a + imm), x32(a - other))
            if (u, sg, add, sb) != exp: bad.append((ln, exp))
        elif op == 'lw':
            off, init = int(t[1]), int(t[2]); mid, pair, l3, l7 = (int(x, 16) for x in t[3:7])
            emid, epair, el3, el7, full7 = ref_lw(off, init)
            if (mid, pair, l3) != (emid, epair, el3) or \
               ((l7 != el7) if full7 else ((l7 & 0xFFFFFFFF) != (el7 & 0xFFFFFFFF))):
                bad.append((ln, (hex(emid), hex(epair), hex(el3), hex(el7))))
        elif op == 'sw':
            off, kind = int(t[1]), t[2]; got = [int(x, 16) for x in t[3:]]
            if got != ref_sw(off, kind): bad.append((ln, ref_sw(off, kind)))
        elif op in ('guard_div', 'guard_divu'):
            a, b = int(t[1], 16), int(t[2], 16); br = int(t[3].split('=')[1])
            want = 1 if (b & 0xFFFFFFFF) == 0 or (op == 'guard_div' and b == M64 and a == 0xFFFFFFFF80000000) else 0
            if br != want: bad.append((ln, f'breaks {want}'))
        else:
            bad.append((ln, 'unknown row'))
    return rows, bad

def main():
    global SEXT
    exe = build()
    lines = subprocess.check_output([exe], text=True).splitlines()
    rows, bad = check(lines)
    real = bad
    for b in real[:30]: print('FAIL', b)
    z = sum(1 for ln in lines if ln.startswith(('ddivu ', 'ddiv ')) and int(ln.split()[2], 16) == 0)
    print(f'rows={rows} mismatches={len(bad)} (of which {z} rows are divisor-0 ddiv/ddivu; s7085 recomp.h fix)')
    SEXT = False
    _, neg = check(lines)
    print(f'negative control (zero-extending reference) mismatches={len(neg)}')
    sys.exit(0 if not real and len(neg) > 0 else 1)

if __name__ == '__main__':
    main()
