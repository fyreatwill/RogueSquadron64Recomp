#!/usr/bin/env python3
"""s7900 G3 island B: diff the port's gfx-task RDRAM (s7751 snapshot) against retail RDRAM rows dumped by the oracle at
osSpTaskLoad (--pc-ram-dump 0x80033E3C:0x80700000:0x80700800 --pc-ram-dump-also 0x80749000:0x8074D000, s7900).
Pairing: for each port snapshot, the retail matrix-pool row with the most 64-byte matrices exactly equal (ties -> smallest
summed |fixed-point diff|). Then per matrix (the drifting instances named by tools/s7900_tri_source.py and every other
matrix as control): equal / LSB (max |diff| <= LSBMAX fixed units) / far, and per mesh block equal or the differing words.
Discrimination: H-matrix = drifting matrices LSB-differ while mesh blocks equal; H-vtx = mesh differs, matrices equal;
H-state = drifting matrices differ far (an object field, not rounding).
Control (same run): the port snapshot with one planted fixed-point unit in one matrix must pair to the same row and report
exactly that matrix as LSB +-1.
usage: s7900_retail_mtx_cmp.py ORACLE.log SNAP.bin [SNAP.bin ...] [--mtx 700100,700140,...] [--mesh 749930,74BE50,...]
"""
import sys, struct, re
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from rs64_zopen import zopen, zbytes
a = sys.argv[1:]
if len(a) < 2: print(__doc__); sys.exit(2)
opt = lambda n: [int(x, 16) for x in a[a.index(n) + 1].split(',')] if n in a else []
DRIFT = set(opt('--mtx')); MESH = opt('--mesh') or [0x749930, 0x74BE50, 0x74C060, 0x74C9A8]
LSBMAX = 64
vals = {a[i + 1] for i, x in enumerate(a[:-1]) if x.startswith('--')}
files = [x for x in a[1:] if not x.startswith('--') and x not in vals]
base = []; also = []   # (vi, n, words)
rx = re.compile(r'^\[ramdump(\d*)\] vi=(\d+) n=(\d+) (?:a=([0-9A-F]+) )?w=([0-9A-F]+)')
with zopen(a[0]) as f:
    for l in f:
        if not l.startswith('[ramdump'): continue
        m = rx.match(l)
        if not m: continue
        w = bytes.fromhex(m.group(5)); row = (int(m.group(2)), int(m.group(3)), w)
        (also if m.group(1) else base).append(row)
print(f'retail rows: pool {len(base)} mesh {len(also)}')
def fx(blk):   # 64-byte N64 fixed matrix -> 16 s15.16 ints
    hi = struct.unpack('>16H', blk[:32]); lo = struct.unpack('>16H', blk[32:])
    return [(((h << 16) | l) ^ 0x80000000) - 0x80000000 for h, l in zip(hi, lo)]
def snap(path):
    b = bytes(zbytes(path)); H = 20 + 4096
    g = lambda ad, n: b''.join(struct.pack('>I', struct.unpack_from('<I', b, H + ad + 4 * i)[0]) for i in range(n // 4))
    return g, struct.unpack_from('<5I', b, 0)
def pair(pool):
    best = None
    for vi, n, w in base:
        eq = sum(pool[i:i + 64] == w[i:i + 64] for i in range(0, 0x800, 64))
        d = sum(sum(abs(x - y) for x, y in zip(fx(pool[i:i + 64]), fx(w[i:i + 64]))) for i in range(0, 0x800, 64))
        k = (eq, -d)
        if best is None or k > best[0]: best = (k, vi, n, w)
    return best
def report(path, pool, g, hdr, quiet=False):
    (eq, negd), vi, n, w = pair(pool)
    out = [f'{path.rsplit("/",1)[-1]} (port vi {hdr[3]}): retail row vi={vi} n={n}: {eq}/32 matrices equal, sum|d|={-negd}']
    cls = {}
    for i in range(0, 0x800, 64):
        ad = 0x700000 + i; p, r = fx(pool[i:i + 64]), fx(w[i:i + 64]); d = [x - y for x, y in zip(p, r)]
        mx = max(abs(x) for x in d); c = 'equal' if mx == 0 else ('LSB' if mx <= LSBMAX else 'far')
        cls[ad] = c
        if c != 'equal' and not quiet:
            out.append(f'  mtx {ad:06X} {"DRIFT" if ad in DRIFT else "other"} {c} max|d|={mx} d={d}')
    dr = [cls[x] for x in sorted(DRIFT) if x in cls]; ot = [cls[x] for x in cls if x not in DRIFT]
    out.append(f'  drift matrices: ' + ' '.join(f'{x:06X}:{cls[x]}' for x in sorted(DRIFT) if x in cls) +
               f' | others equal {ot.count("equal")}/{len(ot)} LSB {ot.count("LSB")} far {ot.count("far")}')
    mrow = None
    for vi2, n2, w2 in also:
        if n2 <= n: mrow = (vi2, n2, w2)
    if mrow and not quiet:
        for ms in MESH:
            pm = g(ms, 64); rm = mrow[2][ms - 0x749000: ms - 0x749000 + 64]
            dif = [(j, pm[j:j + 4].hex(), rm[j:j + 4].hex()) for j in range(0, 64, 4) if pm[j:j + 4] != rm[j:j + 4]]
            out.append(f'  mesh {ms:06X} (retail row n={mrow[1]}): ' + ('equal' if not dif else f'{len(dif)}/16 words differ {dif[:4]}'))
    return cls, out
for p in files:
    g, hdr = snap(p); pool = g(0x700000, 0x800)
    cls, out = report(p, pool, g, hdr); print('\n'.join(out))
# control: plant +1 fixed unit (frac LSB of element 12) in the first non-drift equal matrix of the last snapshot
eqs = [x for x in sorted(cls) if cls[x] == 'equal']
if eqs:
    t = eqs[0] - 0x700000; pl = bytearray(pool); o = t + 32 + 24; v = struct.unpack_from('>H', pl, o)[0]; struct.pack_into('>H', pl, o, (v + 1) & 0xFFFF)
    c2, _ = report('control', bytes(pl), g, hdr, quiet=True)
    ch = [x for x in c2 if c2[x] != cls[x]]
    ok = ch == [eqs[0]] and c2[eqs[0]] == 'LSB'
    print(f'control: planted +1 in {eqs[0]:06X} -> changed {[hex(x) for x in ch]} -> {"PASS" if ok else "FAIL"}')
