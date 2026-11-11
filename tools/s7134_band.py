#!/usr/bin/env python3
"""s7134: per-swap triangle vertex list of a ROGUESQ_G5B_FRAME capture, with the texture image / combiner state each tri is drawn under,
plus a coverage PNG (each tri group coloured; holes = black). usage: s7134_band.py cap swap outprefix [first_tri last_tri]"""
import sys, struct
cap, want, outp = sys.argv[1], int(sys.argv[2]), sys.argv[3]
lo_t, hi_t = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (0, 1 << 30)
f = open(cap, 'rb'); act = False; tris = []; state = {'timg': 0, 'cc': 0, 'om': 0, 'cimg': 0}
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
        if op == 0x3D: state['timg'] = rw(a + 4) & 0xFFFFFF
        if op == 0x3C: state['cc'] = ((w0 & 0xFFFFFF) << 32) | rw(a + 4)
        if op == 0x2F: state['om'] = ((w0 & 0xFFFFFF) << 32) | rw(a + 4)
        if op == 0x3F: state['cimg'] = rw(a + 4) & 0xFFFFFF
        if 8 <= op <= 15 and a + l <= n:
            w1 = rw(a + 4); sx = lambda v, b: (v & ((1 << b) - 1)) - ((1 << b) if v & (1 << (b - 1)) else 0)
            yl = sx(w0, 14) / 4; ym = sx(w1 >> 16, 14) / 4; yh = sx(w1, 14) / 4
            XL, DXL = s32(rw(a + 8)) / 65536, s32(rw(a + 12)) / 65536; XH, DXH = s32(rw(a + 16)) / 65536, s32(rw(a + 20)) / 65536
            XM, DXM = s32(rw(a + 24)) / 65536, s32(rw(a + 28)) / 65536; lft = (w0 >> 23) & 1
            # vertices: top (XH at yh), mid (XL at ym), bottom (XH + DXH*(yl-yh))
            v = [(XH, yh), (XL, ym), (XH + DXH * (yl - int(yh)), yl)]
            tris.append(dict(i=len(tris), op=op, lft=lft, v=v, yh=yh, ym=ym, yl=yl, XH=XH, DXH=DXH, XM=XM, DXM=DXM, XL=XL, DXL=DXL,
                             timg=state['timg'], cc=state['cc'], om=state['om'], cimg=state['cimg']))
        a += l
W, H = 1024, 448
import zlib
cov = [[None] * W for _ in range(H)]
for t in tris:
    if not (lo_t <= t['i'] <= hi_t): continue
    for y in range(max(0, int(t['yh'])), min(H, int(t['yl']) + 1)):
        yc = y + 0.5
        if not (t['yh'] <= yc < t['yl']): continue
        xh = t['XH'] + t['DXH'] * (yc - int(t['yh']))
        xo = t['XM'] + t['DXM'] * (yc - int(t['yh'])) if yc < t['ym'] else t['XL'] + t['DXL'] * (yc - t['ym'])
        a_, b_ = sorted((xh, xo))
        for x in range(max(0, int(a_)), min(W, int(b_) + 1)):
            if a_ <= x + 0.5 < b_: cov[y][x] = t['i']
def col(i):
    if i is None: return (0, 0, 0)
    h = (i * 2654435761) & 0xFFFFFF; return (64 + (h & 0x7F), 64 + (h >> 8 & 0x7F), 64 + (h >> 16 & 0x7F))
raw = b''.join(b'\0' + bytes(c for x in range(W) for c in col(cov[y][x])) for y in range(H))
def chunk(k, d): return struct.pack('>I', len(d)) + k + d + struct.pack('>I', zlib.crc32(k + d) & 0xFFFFFFFF)
open(outp + '.png', 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))
with open(outp + '.txt', 'w') as o:
    for t in tris:
        o.write('#%d op%X cimg %06X timg %06X cc %014X om %014X v %s\n' % (t['i'], t['op'], t['cimg'], t['timg'], t['cc'], t['om'],
                ' '.join('(%.1f,%.1f)' % p for p in t['v'])))
print('tris', len(tris))
