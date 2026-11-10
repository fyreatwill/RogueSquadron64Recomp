#!/usr/bin/env python3
"""s7084: compile fpu_test.c with the live RecompiledFuncs flags (-O2, recomp.h from lib/), run it,
and compare every row against an exact MIPS R4300 reference (FCSR RM 0=nearest-even, 1=toward zero,
2=+inf, 3=-inf; trunc always toward zero; cvt.s.d rounds per RM, overflow with EO off -> inf/max).
Negative control: the same rows checked against a reference that IGNORES the mode (always RN) must
mismatch on the RZ/RP/RM rows; if it does not, the test cannot see a hoisted conversion.
Exit 0 iff real reference matches every row and the negative control mismatches >0 rows."""
import os, subprocess, sys, math
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'scratch', 's7084')

def build():
    os.makedirs(OUT, exist_ok=True)
    exe = os.path.join(OUT, 'fpu_test')
    inc = [os.path.join(ROOT, p) for p in ('include', 'lib/N64ModernRuntime/ultramodern/include',
           'lib/N64ModernRuntime/librecomp/include', 'lib/N64ModernRuntime/N64Recomp/include')]
    cmd = ['cc', '-g', '-std=gnu17', '-arch', 'arm64', '-O2', '-fno-strict-aliasing', '-w',
           '-Wno-implicit-function-declaration'] + sum((['-I', i] for i in inc), []) + \
          [os.path.join(HERE, 'fpu_test.c'), '-o', exe]
    subprocess.check_call(cmd)
    return exe

def rnd_int(x, mode):
    if mode == 1: return math.trunc(x)
    if mode == 2: return math.ceil(x)
    if mode == 3: return math.floor(x)
    fl = math.floor(x); r = x - fl
    if r > F(1, 2): return fl + 1
    if r < F(1, 2): return fl
    return fl if fl % 2 == 0 else fl + 1

FMAX = (2 - F(1, 2**23)) * F(2)**127
def rnd_f32(x, mode):
    if x == 0: return 0.0
    s = -1 if x < 0 else 1; a = abs(x)
    e = math.floor(math.log2(a))
    while F(2)**e > a: e -= 1
    while F(2)**(e + 1) <= a: e += 1
    e = max(e, -126)
    q = F(2)**(e - 23)
    m = a / q
    # direction relative to magnitude
    mm = {0: 0, 1: 1, 2: 2 if s > 0 else 3, 3: 3 if s > 0 else 2}[mode]
    k = rnd_int(m, mm)
    v = k * q
    if v > FMAX:
        return s * (float('inf') if mm in (0, 2) else float(FMAX))
    return s * float(v)

def ref(op, mode, x):
    if op in ('cvt.w.d', 'cvt.w.s'): return rnd_int(x, mode)
    if op == 'trunc.w.s': return math.trunc(x)
    if op == 'ceil.w.d': return math.ceil(x)
    if op == 'cvt.s.d': return rnd_f32(x, mode)

def main():
    exe = build()
    lines = subprocess.check_output([exe], text=True).splitlines()
    bad = neg = rows = 0
    for ln in lines:
        t = ln.split()
        if t[0] == 'final_cs':
            if t[1] != '0': print('FAIL final_cs', t[1]); bad += 1
            continue
        op, mode, x = t[0], int(t[1]), F(float.fromhex(t[2]))
        got = float.fromhex(t[3]) if op == 'cvt.s.d' else int(t[3])
        rows += 1
        exp = ref(op, mode, x)
        if len(t) > 4 and t[4] != f'cs={mode}': print('FAIL cs', ln); bad += 1
        if got != exp: print('FAIL', ln, 'expected', exp); bad += 1
        if op.startswith('cvt') and mode != 0 and got != ref(op, 0, x): neg += 1
    print(f'rows={rows} mismatches={bad} negative_control_mismatches={neg}')
    sys.exit(0 if bad == 0 and neg > 0 else 1)

if __name__ == '__main__':
    main()
