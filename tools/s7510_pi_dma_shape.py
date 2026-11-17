#!/usr/bin/env python3
"""s7510 class FG: PI cart->RDRAM DMA shape vs hardware.

Reads game logs captured with ROGUESQ_LOG_DMA=1 and classifies every ROM->RDRAM copy (`[rom-read]` lines, one per
recomp::do_rom_read call, i.e. every copy that passed the s5061 guard) against a hardware model of the PI.

Hardware model = mupen64plus-core pi_controller.c dma_pi_write (rs64-oracle checkout), which encodes n64brew
"Peripheral Interface / Unaligned DMA transfer": cart &= ~1, dram &= 0xFFFFFE, len = WR_LEN + 1 (libultra writes
size - 1, so len = size); if len >= 0x7F and odd: len += 1; if len <= 0x80: len -= dram & 7 (clamped at 0).
Our runtime copies exactly size bytes from cart to dram, byte for byte (pi.cpp do_rom_read).
A copy is EQUAL when both models write the same bytes from the same ROM offsets to the same RDRAM addresses.

usage: s7510_pi_dma_shape.py [--controls] LOG...   rc 0 = every live copy EQUAL and controls pass; 1 = live diffs; 3 = control FAIL
"""
import re, sys
from collections import Counter, defaultdict

RR = re.compile(r'\[rom-read\] phys=0x([0-9A-Fa-f]+) ram=0x([0-9A-Fa-f]+) bytes=0x([0-9A-Fa-f]+)')
PS = re.compile(r'\[pi-start-dma\] ra=0x([0-9A-Fa-f]+) .*dir=(\d+) dram=0x([0-9A-Fa-f]+) size=0x([0-9A-Fa-f]+)')
GD = re.compile(r'\[s5061-pi-dma-guard\]')


def hw(cart, dram, size, round_odd=True, shrink=True):
    c = cart & ~1
    d = dram & 0xFFFFFE
    n = size
    if round_odd and n >= 0x7F and (n & 1):
        n += 1
    if shrink and n <= 0x80:
        n = n - (d & 7) if n >= (d & 7) else 0
    return c, d, n


def ours(cart, dram, size):
    return cart, dram & 0xFFFFFF, size


def shape(cart, dram, size):
    k = []
    if cart & 1: k.append('cart_odd')
    if dram & 1: k.append('dram_odd')
    elif dram & 7: k.append('dram_mis8')
    if size & 1: k.append('size_odd')
    if size == 0: k.append('size0')
    return '+'.join(k) or 'canon'


def equal(cart, dram, size, **kw):
    phys = dram & 0x1FFFFFFF
    return hw(cart, phys, size, **kw) == ours(cart, phys, size)


def controls():
    ok = True
    syn = [  # (cart, dram, size, expected shape, expected equal)
        (0x10001000, 0x80100000, 0x1000, 'canon', True),
        (0x10001001, 0x80100000, 0x1000, 'cart_odd', False),
        (0x10001000, 0x80100001, 0x1000, 'dram_odd', False),
        (0x10001000, 0x80100004, 0x40, 'dram_mis8', False),    # short + misaligned: hw shrinks by 4
        (0x10001000, 0x80100004, 0x1000, 'dram_mis8', True),   # long misaligned: model copies the full length
        (0x10001000, 0x80100000, 0x81, 'size_odd', False),     # odd >= 0x7F: hw +1
        (0x10001000, 0x80100000, 0x7D, 'size_odd', True),      # odd < 0x7F: hw copies size bytes
    ]
    for c, d, n, es, ee in syn:
        s, e = shape(c, d, n), equal(c, d, n)
        if s != es or e != ee:
            ok = False
            print(f'CONTROL FAIL synthetic cart={c:08X} dram={d:08X} size={n:X} shape={s}/{es} equal={e}/{ee}')
    # mutation controls: dropping each hardware rule must flip exactly its synthetic case
    if not equal(0x10001000, 0x80100000, 0x81, round_odd=False): ok = False; print('CONTROL FAIL mutant round_odd')
    if not equal(0x10001000, 0x80100004, 0x40, shrink=False): ok = False; print('CONTROL FAIL mutant shrink')
    print(f'controls {"PASS" if ok else "FAIL"} ({len(syn)} synthetic + 2 mutants)')
    return ok


def main(argv):
    ctl = '--controls' in argv
    logs = [a for a in argv if not a.startswith('--')]
    rc = 0
    if ctl and not controls():
        rc = 3
    for path in logs:
        shapes, diffs, sizes = Counter(), Counter(), Counter()
        ras = defaultdict(Counter)
        ex = {}
        n = ps = guard = 0
        last_ra = None
        with open(path, 'rb') as f:
            for raw in f:
                if b'[rom-read]' not in raw and b'[pi-start-dma]' not in raw and b'[s5061-pi' not in raw:
                    continue
                line = raw.decode('latin-1')
                m = PS.search(line)
                if m:
                    ps += 1; last_ra = int(m.group(1), 16); continue
                if GD.search(line):
                    guard += 1; continue
                m = RR.search(line)
                if not m:
                    continue
                cart, dram, size = (int(g, 16) for g in m.groups())
                n += 1
                s = shape(cart, dram, size)
                shapes[s] += 1
                if not equal(cart, dram, size):
                    key = (s, size if size <= 0x80 else -1)
                    diffs[s] += 1
                    ras[s][last_ra] += 1
                    ex.setdefault(key, (cart, dram, size, last_ra))
        print(f'== {path}')
        print(f'   rom_reads={n} pi_start_dma={ps} guard_lines={guard} shapes={dict(shapes)} diffs={dict(diffs)}')
        for (s, _), (c, d, z, ra) in sorted(ex.items())[:20]:
            h = hw(c, d & 0x1FFFFFFF, z)
            print(f'   DIFF {s}: cart={c:08X} dram={d:08X} size={z:X} -> hw cart={h[0]:08X} dram={h[1]:06X} len={h[2]:X} last_pi_ra={ra and hex(ra)}')
        for s, c in ras.items():
            print(f'   {s} by last osPiStartDma ra: ' + ' '.join(f'{(r or 0):08X}x{k}' for r, k in c.most_common(8)))
        if n == 0:
            print('   CONTROL FAIL: no [rom-read] lines (ROGUESQ_LOG_DMA not armed?)'); rc = 3
        elif diffs and rc == 0:
            rc = 1
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
