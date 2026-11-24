#!/usr/bin/env python3
"""s7902 G3 island B: diff the port's per-frame dynamic vertex arena 0x749000-0x74D000 (s7751 task snapshot) against every
retail arena row the oracle dumped at osSpTaskLoad (--pc-ram-dump-also 0x80749000:0x8074D000, s7900 r1).
Per snapshot: the retail row paired by matrix pool (as tools/s7900_retail_mtx_cmp.py), the word diff of the arena vs that row,
the differing 64-byte blocks, and the retail row with the FEWEST differing words (whole arena and per differing block).
Discrimination for the crawl-tail odd-frame residual:
  H-draw  : each differing port block equals the same block of a DIFFERENT retail row (adjacent frame) -> timing/buffer pairing.
  H-value : the differing port block matches no retail row within +-W rows -> the port wrote values retail never wrote there.
  H-clip  : arena equal to the paired row on the odd frames too -> the diff is downstream of RDRAM (RSP/clip).
Control (same run): the last snapshot with one planted arena word must add exactly that one word to its paired-row diff.
usage: s7902_arena_cmp.py ORACLE.log SNAP.bin [SNAP.bin ...] [--win 12]
"""
import sys, struct, re
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from rs64_zopen import zopen, zbytes
a = sys.argv[1:]
if len(a) < 2: print(__doc__); sys.exit(2)
W = int(a[a.index('--win') + 1]) if '--win' in a else 12
files = [x for i, x in enumerate(a[1:], 1) if not x.startswith('--') and a[i - 1] != '--win']
A0, AN = 0x749000, 0x4000
base, also = [], []
rx = re.compile(r'^\[ramdump(\d*)\] vi=(\d+) n=(\d+) (?:a=([0-9A-F]+) )?w=([0-9A-F]+)')
with zopen(a[0]) as f:
    for l in f:
        if not l.startswith('[ramdump'): continue
        m = rx.match(l)
        if not m: continue
        row = (int(m.group(2)), int(m.group(3)), bytes.fromhex(m.group(5)))
        (also if m.group(1) else base).append(row)
also = [r for r in also if len(r[2]) >= AN]
print(f'retail rows: pool {len(base)} arena {len(also)} (vi {also[0][0]}..{also[-1][0]})' if also else 'no arena rows')
def fx(blk):
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
        if best is None or (eq, -d) > best[0]: best = ((eq, -d), vi, n)
    return best
def wdiff(x, y, lo=0, hi=AN): return [j for j in range(lo, hi, 4) if x[j:j + 4] != y[j:j + 4]]
def arena_row(n):   # the arena row of the same osSpTaskLoad hit (largest n2 <= n)
    k = None
    for i, r in enumerate(also):
        if r[1] <= n: k = i
    return k
def analyse(name, ar, pool, quiet=False):
    (eq, nd), vi, n = pair(pool); k = arena_row(n)
    if k is None: return None, [f'{name}: no arena row']
    d = wdiff(ar, also[k][2]); out = [f'{name}: pool pair vi={vi} n={n} ({eq}/32 mtx equal, sum|d|={-nd}); arena row vi={also[k][0]} n={also[k][1]}: {len(d)} words differ']
    if quiet: return d, out
    near = sorted(((len(wdiff(ar, also[i][2])), i) for i in range(max(0, k - W), min(len(also), k + W + 1))))[:3]
    out.append('  nearest whole-arena rows: ' + ' '.join(f'vi={also[i][0]}(k{i - k:+d}):{c}' for c, i in near))
    blocks = sorted({j & ~63 for j in d})
    for bo in blocks[:24]:
        bd = wdiff(ar, also[k][2], bo, bo + 64)
        best = sorted((len(wdiff(ar, also[i][2], bo, bo + 64)), abs(i - k), i) for i in range(max(0, k - W), min(len(also), k + W + 1)))[0]
        zs = lambda b: ' '.join('%6d' % struct.unpack('>h', b[bo + 8 * v + 4: bo + 8 * v + 6])[0] for v in range(8))
        out.append(f'  blk {A0 + bo:06X}: {len(bd)}/16 words differ; best row k{best[2] - k:+d} vi={also[best[2]][0]} -> {best[0]} differ')
        out.append('      words (off port/retail): ' + ' '.join(f'+{j - bo:02X} {ar[j:j + 4].hex()}/{also[k][2][j:j + 4].hex()}' for j in bd))
        out.append(f'      port   z: {zs(ar)}')
        out.append(f'      retail z: {zs(also[k][2])}')
        if best[0] == 0 and best[2] != k: out.append(f'      (exact in retail row k{best[2] - k:+d})')
    if len(blocks) > 24: out.append(f'  ... {len(blocks)} blocks')
    return d, out
last = None
for p in files:
    g, hdr = snap(p); ar = g(A0, AN); pool = g(0x700000, 0x800)
    d, out = analyse(p.rsplit('/', 1)[-1] + f' (serial {hdr[2]})', ar, pool); print('\n'.join(out)); last = (ar, pool, d)
if last and last[2] is not None:
    ar, pool, d = last; pl = bytearray(ar); o = next(j for j in range(0, AN, 4) if j not in set(d)); pl[o] ^= 0x01
    d2, _ = analyse('control', bytes(pl), pool, quiet=True)
    ok = sorted(set(d2) - set(d)) == [o] and set(d) <= set(d2)
    print(f'control: planted 1 bit at {A0 + o:06X} -> diff {len(d)} -> {len(d2)} words -> {"PASS" if ok else "FAIL"}')
