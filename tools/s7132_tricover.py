#!/usr/bin/env python3
"""s7132: which RDP triangles of one swap of a ROGUESQ_G5B_FRAME stream cover given pixels (edge-walk approximation, s15.16 X, s11.2 Y).
usage: s7132_tricover.py cap swap x,y [x,y ...]   prints every tri covering each point + global coordinate-range census for that swap"""
import sys, struct
cap, want = sys.argv[1], int(sys.argv[2]); pts = [tuple(map(float, a.split(','))) for a in sys.argv[3:]]
f = open(cap, 'rb'); sw = -1; tris = []; rects = []; cimgs = []; act = False
def s32(v): return v - (1 << 32) if v & 0x80000000 else v
while True:
    t = f.read(4)
    if len(t) < 4: break
    tag = struct.unpack('<I', t)[0]
    if tag == 0x50415753:
        _, sw = struct.unpack('<QI', f.read(12))
        if sw > want: break
        act = sw == want; continue
    if tag == 0x204D4152: f.seek(0x1000000, 1); continue
    lo, n = struct.unpack('<II', f.read(8))
    if not act: f.seek(n, 1); continue
    c = f.read(n); a = 0
    rw = lambda o: struct.unpack('<I', c[o:o + 4])[0]
    while a + 8 <= n:
        w0 = rw(a); op = (w0 >> 24) & 0x3F; l = 8
        if 8 <= op <= 15: l = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
        elif op in (0x24, 0x25): l = 16
        if 8 <= op <= 15 and a + l <= n:
            w1 = rw(a + 4); sx = lambda v, b: (v & ((1 << b) - 1)) - ((1 << b) if v & (1 << (b - 1)) else 0)
            yl = sx(w0, 14) / 4; ym = sx(w1 >> 16, 14) / 4; yh = sx(w1, 14) / 4
            XL, DXL = s32(rw(a + 8)) / 65536, s32(rw(a + 12)) / 65536; XH, DXH = s32(rw(a + 16)) / 65536, s32(rw(a + 20)) / 65536
            XM, DXM = s32(rw(a + 24)) / 65536, s32(rw(a + 28)) / 65536; lft = (w0 >> 23) & 1
            tris.append((len(tris), lo + a, op, lft, yh, ym, yl, XH, DXH, XM, DXM, XL, DXL))
        if op in (0x24, 0x25, 0x36):
            w1 = rw(a + 4); rects.append((op, (w1 >> 12 & 0xFFF) / 4, (w1 & 0xFFF) / 4, (w0 >> 12 & 0xFFF) / 4, (w0 & 0xFFF) / 4))
        if op == 0x3F: cimgs.append((w0 & 0x3FF) + 1)
        a += l
yh0 = lambda y: int(y)  # RDP: XH/XM start at the integer scanline of YH; XL at YM
def cover(tr, x, y):
    i, ad, op, lft, yh, ym, yl, XH, DXH, XM, DXM, XL, DXL = tr
    if not (yh <= y < yl): return False
    xh = XH + DXH * (y - int(yh)); xo = XM + DXM * (y - int(yh)) if y < ym else XL + DXL * (y - ym)
    lo_, hi_ = (xh, xo) if not lft else (xo, xh)
    return min(lo_, hi_) <= x < max(lo_, hi_) if True else False
print('swap', want, 'tris', len(tris), 'rects', len(rects), 'cimg widths', sorted(set(cimgs)))
for x, y in pts:
    hit = [t for t in tris if cover(t, x, y)]
    print('pt', x, y, 'covered by', len(hit))
    rh = [r for r in rects if r[1] <= x < r[3] + 1 and r[2] <= y < r[4] + 1]
    print('   rects covering', len(rh), rh[:6])
    for t in hit[:12]: print('  #%d @%06X op%X lft%d y %.2f/%.2f/%.2f XH %.2f d%.3f XM %.2f d%.3f XL %.2f d%.3f' % t)
import collections
big = [t for t in tris if max(abs(t[7]), abs(t[9]), abs(t[11])) > 2047 or min(t[4], t[5], t[6]) < -1024 or t[6] > 1500]
print('extreme tris (|X|>2047 or y<-1024 or yl>1500):', len(big))
for t in big[:15]: print('  #%d @%06X op%X lft%d y %.2f/%.2f/%.2f XH %.2f d%.3f XM %.2f d%.3f XL %.2f d%.3f' % t)
