#!/usr/bin/env python3
"""s7912 G3: name the element behind a det-pair island: for every triangle, its RDP draw context (last SetTextureImage
address/fmt/width, SetCombine, SetOtherModes, SetPrimColor, SetEnvColor, the tri opcode) and screen bbox; then per frame
of an island, the port-only / retail-only tris (multiset on exact edge coefficients) grouped by context.
Control (iron rule 1, same run): a frame from the pre-island exact window must give 0 port-only/0 retail-only, and a planted
YH+1 on one tri of it must give exactly 1/1 in that tri's context group. rc 3 if a control fails.
usage: s7912_island_ctx.py RETAIL.bin PORT.bin LAG(=port-retail index, s7911 convention) J0 J1 CTRL_J [--prim FFFFFFFF]
"""
import struct, sys, collections, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rs64_zopen import zbytes
a = sys.argv[1:]
if len(a) < 6: print(__doc__); sys.exit(2)
PRIMF = a[a.index('--prim') + 1] if '--prim' in a else None
def frames(path, retail):
    f = bytes(zbytes(path)); H = 20 if retail else 16; o = 0; buf = bytearray()
    while o + H <= len(f):
        w = struct.unpack_from('<5I' if retail else '<4I', f, o); ln = w[3] if retail else w[2]
        buf += f[o + H:o + H + ln]; o += H + ln
    cat = bytes(buf); del f, buf; g = lambda i: struct.unpack_from('<I', cat, i)[0]
    out = []; cur = []; st = {}; x = 0
    while x + 8 <= len(cat):
        w0, w1 = g(x), g(x + 4); op = (w0 >> 24) & 0x3F; n = 8
        if 0x08 <= op <= 0x0F:
            if x + 32 > len(cat): break
            n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
            e = tuple(g(x + i) for i in range(0, 32, 4))
            yl = (e[0] >> 0) & 0x3FFF; ym = (e[1] >> 16) & 0x3FFF; yh = e[1] & 0x3FFF
            xh = struct.unpack('>i', struct.pack('>I', e[4]))[0] / 65536.0
            ctx = (op, st.get(0x3D), st.get(0x3C), st.get(0x2F), st.get(0x3A), st.get(0x3B))
            cur.append((e + (w0 & 0x3FFF,), ctx, (yh / 4.0, yl / 4.0, xh)))
        elif op in (0x24, 0x25):
            n = 16; cur.append(((0x100 | op, w0, w1), ('texrect', st.get(0x3D), None, None, st.get(0x3A), None), (0, 0, 0)))   # keeps frame indexing = s7821
        elif op == 0x29:
            if cur: out.append(cur)
            cur = []
        elif op == 0x3D: st[0x3D] = '%06X/f%d/s%d/w%d' % (w1 & 0xFFFFFF, (w0 >> 21) & 7, (w0 >> 19) & 3, (w0 & 0x3FF) + 1)
        elif op == 0x3C: st[0x3C] = '%06X%08X' % (w0 & 0xFFFFFF, w1)
        elif op == 0x2F: st[0x2F] = '%06X%08X' % (w0 & 0xFFFFFF, w1)
        elif op == 0x3A: st[0x3A] = '%08X' % w1
        elif op == 0x3B: st[0x3B] = '%08X' % w1
        x += n
    return out
lag, j0, j1, cj = map(int, a[2:6])
R = frames(a[0], True); P = frames(a[1], False)
print(f'frames retail {len(R)} port {len(P)} lag {lag}')
def diff(p, r):
    pc = collections.Counter(t[0] for t in p); rc = collections.Counter(t[0] for t in r)
    po = pc - rc; ro = rc - pc
    cx = {t[0]: (t[1], t[2]) for t in p}; cx.update({t[0]: (t[1], t[2]) for t in r if t[0] not in cx})
    return po, ro, cx
# controls
po, ro, _ = diff(P[cj], R[cj - lag]); ok1 = not po and not ro
pl = list(P[cj]); k = next((i for i, t in enumerate(pl) if PRIMF is None or t[1][4] == PRIMF), 0)
t = pl[k]; e = list(t[0]); e[1] = (e[1] & ~0x3FFF) | ((e[1] + 1) & 0x3FFF); pl[k] = (tuple(e), t[1], t[2])
po2, ro2, _ = diff(pl, R[cj - lag]); ok2 = sum(po2.values()) == 1 and sum(ro2.values()) == 1
print(f'control exact frame {cj}: {"PASS" if ok1 else "FAIL"} (po {sum(po.values())} ro {sum(ro.values())}); plant YH+1: {"PASS" if ok2 else "FAIL"}')
# context census of the island
agg = collections.Counter(); aggr = collections.Counter(); ctxs_all = collections.Counter(); rows = []
for j in range(j0, min(j1, len(P))):
    if not 0 <= j - lag < len(R): break
    po, ro, cx = diff(P[j], R[j - lag])
    for e, n in po.items(): agg[cx[e][0]] += n
    for e, n in ro.items(): aggr[cx[e][0]] += n
    for tt in P[j]: ctxs_all[tt[1]] += 1
    if (j - j0) % 30 == 0:
        ys = sorted(cx[e][1] for e in po)
        rows.append((j, sum(po.values()), sum(ro.values()), len(P[j]), len(R[j - lag]), ys[:3]))
print('island frames (j, port-only, retail-only, ntri P, ntri R, first bboxes yh,yl,xh):')
for r in rows: print('  ', r)
print('port-only by context (op, teximg, combine, othermodes, prim, env):')
for c, n in agg.most_common(8): print(f'  {n:6d}  {c}   [all-tris in ctx over island: {ctxs_all[c]}]')
print('retail-only by context:')
for c, n in aggr.most_common(8): print(f'  {n:6d}  {c}')
sys.exit(0 if ok1 and ok2 else 3)
