#!/usr/bin/env python3
"""s6850: streaming scan of a port RDP bin (RS64_RDP_BIN_PORT, RS64_RDP_BIN_PORT_VI=1) for x-wrapped rects on wide
colour images.  Flags, per fill (0x36) and texrect (0x24/0x25):
  ZERO-W  fill with ul.x 0 and lr.x field 0 but lr.y > ul.y (the s6848 emitColorFillRect (W&0x3FF)<<14 wrap);
  WRAP    lr.x < ul.x with lr.y > ul.y (a 12-bit 10.2 x field that overflowed: the s6844 wipe shape);
  WRAPOFF a WRAP whose ul.x is already >= the colour-image width (invisible with or without the wrap: s6850 boot
          cinematic particles on the 768-wide image);
  OFFIMG  ul.x >= colour-image width (drawn entirely past the right edge).
Hits are split by whether their VI lies inside the positive-control window (--ctl lo:hi, the ROGUESQ_S6848_FORCE_OVL
window run with ROGUESQ_G1D_OVL_WRAP=0, which must yield ZERO-W fills).  usage: g1d_rectscan.py bin [--ctl lo:hi]"""
import struct, sys, collections
path = sys.argv[1]; clo, chi = 0, -1
if '--ctl' in sys.argv:
    clo, chi = map(int, sys.argv[sys.argv.index('--ctl') + 1].split(':'))
ci = (0, 0); nrec = 0; vmin = 1 << 31; vmax = -1
cwv = {}; n = collections.Counter(); hits = collections.Counter(); first = {}
with open(path, 'rb') as f:
    while True:
        h = f.read(16)
        if len(h) < 16: break
        mg, x, ln, vi = struct.unpack('<4I', h); b = f.read(ln)
        if len(b) < ln: break
        nrec += 1; vmin = min(vmin, vi); vmax = max(vmax, vi); a = 0
        while a + 8 <= len(b):
            w0, w1 = struct.unpack_from('<II', b, a); op = (w0 >> 24) & 0x3F; step = 8
            if 0x08 <= op <= 0x0F: step = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
            elif op in (0x24, 0x25): step = 16
            elif op == 0x3F:
                ci = (w1 & 0xFFFFFF, (w0 & 0x3FF) + 1); r = cwv.setdefault(ci[1], [vi, vi]); r[1] = vi
            if op in (0x24, 0x25, 0x36):
                kind = 'fill' if op == 0x36 else 'texr'; n[(kind, ci[1])] += 1
                lrx, lry, ulx, uly = (w0 >> 12) & 0xFFF, w0 & 0xFFF, (w1 >> 12) & 0xFFF, w1 & 0xFFF
                flag = None
                if op == 0x36 and ulx == 0 and lrx == 0 and lry > uly: flag = 'ZERO-W'
                elif lrx < ulx and lry > uly: flag = 'WRAPOFF' if ulx >= ci[1] * 4 else 'WRAP'
                elif ulx >= ci[1] * 4: flag = 'OFFIMG'
                if flag:
                    zone = 'ctl' if clo <= vi <= chi else 'out'
                    k = (zone, flag, kind, ci[1], ulx, uly, lrx, lry); hits[k] += 1; first.setdefault(k, vi)
            a += step
print('records %d vi %d..%d ctl %d:%d' % (nrec, vmin, vmax, clo, chi))
print('cw VI ranges:', ' '.join('%d:%d..%d' % (k, v[0], v[1]) for k, v in sorted(cwv.items())))
print('rects by (kind, cw):', ' '.join('%s/%d=%d' % (k[0], k[1], c) for k, c in sorted(n.items())))
for z in ('ctl', 'out'):
    for fl in ('ZERO-W', 'WRAP', 'WRAPOFF', 'OFFIMG'):
        t = sum(c for k, c in hits.items() if k[0] == z and k[1] == fl)
        print('%s %-6s total %d' % (z, fl, t))
print('  zone flag   kind   cw    ul.x   ul.y    lr.x   lr.y  count firstVI')
rows = sorted(hits.items(), key=lambda kv: (kv[0][1] in ('OFFIMG', 'WRAPOFF'), kv[0][0], -kv[1], first[kv[0]]))
for k, c in [r for r in rows if r[0][1] not in ('OFFIMG', 'WRAPOFF')][:80] + [r for r in rows if r[0][1] in ('OFFIMG', 'WRAPOFF')][:8]:
    print('  %s %-6s %s %4d %7.2f %6.2f %7.2f %6.2f %6d %7d' % (k[0], k[1], k[2], k[3], k[4] / 4, k[5] / 4, k[6] / 4, k[7] / 4, c, first[k]))
