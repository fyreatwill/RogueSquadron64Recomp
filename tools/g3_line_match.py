#!/usr/bin/env python3
"""s6799 G3: match a thin line seen in a window capture to the RDP triangle(s) that draw it.

Line pixels = non-sky pixels whose neighbours 3 px above AND below are sky-blue (thin dark stroke over sky), in the
capture's picture area mapped onto the 512x448 flight colour image. Each triangle in port-dump records with stamp in
[VI0-W, VI0+W] is drawn (PIL polygon, filled+outline) and scored by hits = its pixels on dilated line pixels;
precision = hits / its pixels. The best triangles name the writer (texture, combiner, vertices, thickness).
Control: --ctl prints the same score for the line pixels shifted 40 FB rows down (must collapse).
usage: g3_line_match.py CAPTURE.png PORT.bin VI0 [--w 150] [--top 12]
"""
import sys, struct, mmap, math
from PIL import Image, ImageDraw, ImageFilter
def arg(n, d):
    a = sys.argv; return type(d)(a[a.index(n) + 1]) if n in a else d
cap, dump, vi0 = sys.argv[1], sys.argv[2], int(sys.argv[3]); W, TOP = arg('--w', 150), arg('--top', 12)
FW, FH = 512, 448
im = Image.open(cap).convert('RGB')
gp = im.convert('L').load(); IW, IH = im.size; ym_ = IH // 2  # picture = non-black span of the middle row (4:3 pillarbox)
x0 = next(x for x in range(IW) if gp[x, ym_] > 12); x1 = next(x for x in range(IW - 1, 0, -1) if gp[x, ym_] > 12) + 1
bx = (x0, 28, x1, IH)  # rows: below the 28 px title bar to the bottom
px = im.load(); sx, sy = FW / (bx[2] - bx[0]), FH / (bx[3] - bx[1])
sky = lambda c: c[2] > c[0] + 25 and c[2] > 110
lum = lambda c: c[0] + c[1] + c[2]
line = Image.new('L', (FW, FH), 0); lp = line.load(); nline = 0
for y in range(bx[1] + 4, bx[3] - 4):  # detect at capture resolution, then map into the 512x448 colour image
    for x in range(bx[0], bx[2]):
        c, u, d = px[x, y], px[x, y - 4], px[x, y + 4]
        if not sky(c) and sky(u) and sky(d) and lum(c) < min(lum(u), lum(d)) - 60:
            fx, fy = int((x - bx[0]) * sx), int((y - bx[1]) * sy)
            if fx > 390 and fy < 160: continue  # radar ring (HUD)
            if not lp[fx, fy]: lp[fx, fy] = 255; nline += 1
line.save(cap.replace('.png', '_linepx.png').replace('/dump/', '/'))
dil = line.filter(ImageFilter.MaxFilter(3)); dp = dil.load()
print('capture %s picture bbox %s line px %d' % (cap, bx, nline))
s14 = lambda v: (((v & 0x3FFF) ^ 0x2000) - 0x2000) / 4.0
s32 = lambda v: (v - (1 << 32) if v & 0x80000000 else v) / 65536.0
fh = open(dump, 'rb'); m = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ); o = 0; res = []; ctl = []
timg = 0; comb = 0; cw = 0
while o + 16 <= len(m):
    _, lo, ln, st = struct.unpack_from('<4I', m, o); d0 = o + 16; o += 16 + ln
    if st < vi0 - W or st > vi0 + W: continue
    a = d0; e = d0 + ln; w = lambda i: struct.unpack_from('<I', m, i)[0]
    while a + 8 <= e:
        w0, w1 = w(a), w(a + 4); op = (w0 >> 24) & 0x3F; L = 8
        if 0x08 <= op <= 0x0F:
            L = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
            yl, ym, yh = s14(w0), s14(w1 >> 16), s14(w1)
            if cw == 512 and yl > yh:
                xl, dl, xh, dh = (s32(w(a + q)) for q in (8, 12, 16, 20))
                A = (xh, yh); B = (xl, ym); C = (xh + dh * (yl - yh), yl)
                if all(-2000 < v < 3000 for p in (A, B, C) for v in p):
                    t = Image.new('L', (FW, FH), 0); ImageDraw.Draw(t).polygon([A, B, C], fill=255, outline=255)
                    bb = t.getbbox()
                    if bb:
                        tp = t.load(); n = hits = hc = 0
                        for y in range(bb[1], bb[3]):
                            for x in range(bb[0], bb[2]):
                                if tp[x, y]:
                                    n += 1; hits += dp[x, y] > 0
                                    if y + 40 < FH: hc += dp[x, y + 40] > 0
                        if hits:
                            Lm = max(math.dist(A, B), math.dist(B, C), math.dist(C, A))
                            th = abs((B[0] - A[0]) * (C[1] - A[1]) - (C[0] - A[0]) * (B[1] - A[1])) / Lm if Lm else 0
                            res.append((hits, hits / n, st, A, B, C, th, timg, comb, n))
                        if hc: ctl.append(hc)
        elif op in (0x24, 0x25): L = 16
        elif op == 0x3F: cw = (w0 & 0x3FF) + 1
        elif op == 0x3D: timg = w1 & 0xFFFFFF
        elif op == 0x3C: comb = '%06X:%08X' % (w0 & 0xFFFFFF, w1)
        a += L
res.sort(key=lambda r: -(r[0] * r[1]))
for r in res[:TOP]:
    print('hits %4d prec %.2f st %d A(%.1f,%.1f) B(%.1f,%.1f) C(%.1f,%.1f) th=%.3f timg=%06X comb=%s px=%d' % (
        r[0], r[1], r[2], *r[3], *r[4], *r[5], r[6], r[7], r[8], r[9]))
print('control (line px shifted +40 rows): best hits %d' % (max(ctl) if ctl else 0))
