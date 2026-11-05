#!/usr/bin/env python3
"""s6898 G5b: streaming scan of a port RDP bin (RS64_RDP_BIN_PORT, RS64_RDP_BIN_PORT_VI=1) for draws that stop at a fixed x.
Per record tracks colour image, scissor, fill colour, prim colour. Reports: scissors by frequency (VI span, draws under it), fill
and texture rects that end at x==--x (default 512) on a wider colour image, and triangles whose right extent sits at --x +-1.
usage: g5b_rdp_edge.py bin [--x 512] [--vi lo:hi] [--every n]"""
import struct, sys, collections
p = sys.argv[1]; X = 512; lo, hi = 0, 1 << 31
if '--x' in sys.argv: X = int(sys.argv[sys.argv.index('--x') + 1])
if '--vi' in sys.argv: lo, hi = map(int, sys.argv[sys.argv.index('--vi') + 1].split(':'))
s16 = lambda v: v - (1 << 32) if v & 0x80000000 else v
ci = (0, 0); sc = None; fill = 0; prim = 0
scs = {}; rects = {}; tris = {}; vmin = 1 << 31; vmax = -1; nrec = 0
with open(p, 'rb') as f:
    while True:
        h = f.read(16)
        if len(h) < 16: break
        mg, x, ln, vi = struct.unpack('<4I', h); b = f.read(ln)
        if len(b) < ln: break
        nrec += 1; vmin = min(vmin, vi); vmax = max(vmax, vi)
        if not lo <= vi <= hi: continue
        a = 0
        while a + 8 <= len(b):
            w0, w1 = struct.unpack_from('<II', b, a); op = (w0 >> 24) & 0x3F; step = 8
            if 0x08 <= op <= 0x0F:
                step = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
                if a + 32 <= len(b):
                    yl = (w0 & 0x3FFF); yl = yl - 0x4000 if yl & 0x2000 else yl
                    ym = (w1 >> 16) & 0x3FFF; ym = ym - 0x4000 if ym & 0x2000 else ym
                    yh = w1 & 0x3FFF; yh = yh - 0x4000 if yh & 0x2000 else yh
                    xl, dl, xh, dh, xm, dm = [s16(v) / 65536 for v in struct.unpack_from('<6I', b, a + 8)]
                    bx = xh + dh * (yl - yh) / 4; mx = xl
                    r = max(xh, bx, mx, xm); l = min(xh, bx, mx, xm)
                    k = sc
                    e = scs.setdefault(k, [vi, vi, 0]); e[1] = vi; e[2] += 1
                    if abs(r - X) <= 1 and ci[1] > X:
                        t = tris.setdefault((ci[1], op, sc, prim), [0, vi, vi, l, r, yh / 4, yl / 4]); t[0] += 1; t[2] = vi
            elif op in (0x24, 0x25): step = 16
            elif op == 0x3F: ci = (w1 & 0xFFFFFF, (w0 & 0x3FF) + 1)
            elif op == 0x2D: sc = ((w0 >> 12) & 0xFFF, w0 & 0xFFF, (w1 >> 12) & 0xFFF, w1 & 0xFFF)
            elif op == 0x37: fill = w1
            elif op == 0x3A: prim = w1
            if op in (0x24, 0x25, 0x36):
                lrx, lry, ulx, uly = (w0 >> 12) & 0xFFF, w0 & 0xFFF, (w1 >> 12) & 0xFFF, w1 & 0xFFF
                if abs(lrx / 4 - X) <= 1 and ci[1] > X:
                    k = (op, ci[1], ulx / 4, uly / 4, lrx / 4, lry / 4, fill if op == 0x36 else prim)
                    e = rects.setdefault(k, [0, vi, vi]); e[0] += 1; e[2] = vi
            a += step
print('records', nrec, 'vi', vmin, vmax)
print('scissors (ulx uly lrx lry /4): first_vi last_vi tris')
for k, e in sorted(scs.items(), key=lambda kv: -kv[1][2])[:24]:
    print(' ', None if k is None else tuple(v / 4 for v in k), e)
print('rects ending at x=%d on a wider image: op cw ulx uly lrx lry colour -> n first last' % X)
for k, e in sorted(rects.items(), key=lambda kv: -kv[1][0])[:30]:
    print(' ', k[:6], '%08X' % k[6], e)
print('tris with right extent at x=%d: cw op scissor prim -> n first last l r yh yl (of first)' % X)
for k, e in sorted(tris.items(), key=lambda kv: -kv[1][0])[:30]:
    print(' ', k[0], hex(k[1]), k[2], '%08X' % k[3], e)
