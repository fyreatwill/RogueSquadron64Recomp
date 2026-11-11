#!/usr/bin/env python3
"""s7166 g3-219-cutscene-hole: per swap of a ROGUESQ_G5B_FRAME capture, which RDP primitives touch a screen region.
usage: s7166_holetris.py cap x0,y0,x1,y1 swap [swap ...]
For every swap: colour image width, FillRects (all, and those overlapping the region), triangles drawn into the main colour image
(the widest one seen in that swap) split by whether their bbox overlaps the region, plus the overlap of their bboxes with it,
grouped by (combiner, othermode hi) so the water/terrain group can be told from sky/HUD.
Triangle bbox from the edge coefficients (YH/YM/YL s11.2, XH/XM/XL s15.16 with slopes), an over-estimate for slivers.
Positive control: a non-hole cutscene swap and a flight swap must list terrain tris in the region."""
import struct, sys
from collections import Counter
cap = sys.argv[1]; R = tuple(map(int, sys.argv[2].split(','))); want = sorted(map(int, sys.argv[3:]))
f = open(cap, 'rb'); sw = -1; out = {}
def s32(v): return v - (1 << 32) if v & 0x80000000 else v
def s14(v): v &= 0x3FFF; return (v - 0x4000 if v & 0x2000 else v) / 4.0
while True:
    t = f.read(4)
    if len(t) < 4: break
    tag = struct.unpack('<I', t)[0]
    if tag == 0x50415753:
        _, sw = struct.unpack('<QI', f.read(12))
        if sw > want[-1]: break
        continue
    if tag == 0x204D4152: f.seek(0x1000000, 1); continue
    lo, n = struct.unpack('<II', f.read(8))
    if sw not in want: f.seek(n, 1); continue
    c = f.read(n); a = 0; o = out.setdefault(sw, {'ci': None, 'cw': {}, 'rects': [], 'tin': Counter(), 'tout': Counter(), 'area': Counter(), 'cc': 0, 'om': 0, 'xr': [1e9, -1e9], 'sc': Counter(), 'cur_sc': None})
    rw = lambda q: struct.unpack('<I', c[q:q + 4])[0]
    while a + 8 <= n:
        w0 = rw(a); op = (w0 >> 24) & 0x3F; l = 8
        if 8 <= op <= 15: l = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
        elif op in (0x24, 0x25): l = 16
        if a + l > n: break
        if op == 0x3F: o['ci'] = rw(a + 4) & 0xFFFFFF; o['cw'][o['ci']] = (w0 & 0x3FF) + 1
        elif op == 0x3C: o['cc'] = ((w0 & 0xFFFFFF) << 32) | rw(a + 4)
        elif op == 0x2F: o['om'] = w0 & 0xFFFFFF
        elif op == 0x2D: w1 = rw(a + 4); o['cur_sc'] = '%d,%d,%d,%d' % (((w0 >> 12) & 0xFFF) >> 2, (w0 & 0xFFF) >> 2, ((w1 >> 12) & 0xFFF) >> 2, (w1 & 0xFFF) >> 2)
        elif op == 0x36:
            w1 = rw(a + 4); r = ((w1 >> 14) & 0x3FF, (w1 >> 2) & 0x3FF, (w0 >> 14) & 0x3FF, (w0 >> 2) & 0x3FF)
            hit = r[0] < R[2] and r[2] > R[0] and r[1] < R[3] and r[3] > R[1]
            o['rects'].append('%06X:%d,%d,%d,%d%s' % (o['ci'] or 0, *r, '*' if hit else ''))
        elif 8 <= op <= 15:
            w1 = rw(a + 4); yl, ym, yh = s14(w0), s14(w1 >> 16), s14(w1)
            xl, dl, xh, dh, xm, dm = (s32(rw(a + 8 + 4 * i)) / 65536.0 for i in range(6))
            xs = [xh, xh + dh * (yl - yh), xm, xm + dm * (ym - yh), xl, xl + dl * (yl - ym)]
            bx0, bx1 = max(-2000, min(xs)), min(4000, max(xs))
            key = (o['ci'], '%014X/%06X' % (o['cc'], o['om']))
            ix = max(0, min(bx1, R[2]) - max(bx0, R[0])); iy = max(0, min(yl, R[3]) - max(yh, R[1]))
            o['sc'][(o['ci'], o['cur_sc'])] += 1
            if ix > 0 and iy > 0: o['tin'][key] += 1; o['area'][key] += ix * iy
            else: o['tout'][key] += 1
            if o['ci'] is not None and ix > 0 and iy > 0: o['xr'][0] = min(o['xr'][0], bx0); o['xr'][1] = max(o['xr'][1], bx1)
        a += l
for s in want:
    o = out.get(s)
    if not o: print(s, 'absent'); continue
    main = max(o['cw'], key=lambda k: (o['cw'][k], sum(v for kk, v in o['tin'].items() if kk[0] == k) + sum(v for kk, v in o['tout'].items() if kk[0] == k))) if o['cw'] else None
    tin = {k[1]: v for k, v in o['tin'].items() if k[0] == main}; tout = {k[1]: v for k, v in o['tout'].items() if k[0] == main}
    area = {k[1]: v for k, v in o['area'].items() if k[0] == main}
    print('swap %d main ci %06X w %s | tris in region %d (bbox-area %.0f) outside %d | rects %d hit %d' % (s, main or 0, o['cw'].get(main), sum(tin.values()), sum(area.values()), sum(tout.values()), len(o['rects']), sum(r.endswith('*') for r in o['rects'])))
    for k in sorted(set(tin) | set(tout), key=lambda k: -(tin.get(k, 0) + tout.get(k, 0)))[:8]:
        print('   %s in %5d (area %8.0f) out %5d' % (k, tin.get(k, 0), area.get(k, 0), tout.get(k, 0)))
    print('   scissors (tris):', ', '.join('%s x%d' % (k[1], v) for k, v in o['sc'].most_common() if k[0] == main))
    print('   rects:', ' '.join(o['rects'])[:700])
