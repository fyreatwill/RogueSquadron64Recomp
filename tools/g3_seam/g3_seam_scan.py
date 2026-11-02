#!/usr/bin/env python3
"""s6793 G3 x=320 centre seam: per frame of a retail (rdplog) or port (RS64_RDP_BIN_PORT) RDP dump, how the scene is
split around column X (default 320). Answers "does the RDP stream itself leave column X uncovered?" without rendering.

  g3_seam_scan.py retail|port DUMP.bin LO HI [--x 320] [--w 640]
      frames LO..HI-1 (FULL_SYNC-delimited, same indices as g3_cine_sweep.py summ), only --w-wide colour images.
      prints: scissor rectangles seen (count), and per frame-class totals of
        straddle  tris whose x extent crosses X (xmin < X-1 and xmax > X+1)
        endL      tris whose right edge ends within [X-2, X+0.5]   (left-half geometry)
        startR    tris whose left edge starts within [X-0.5, X+2]  (right-half geometry)
        rect@X    texrects/fillrects with an edge within [X-2, X+2]
      plus the exact right/left edge x values (0.25 px bins) of endL/startR tris, so a 1-px gap between the halves
      (e.g. left ends at 319.0, right starts at 320.0 vs 321.0) is visible directly.
"""
import struct, sys, collections
sys.path.insert(0, __file__.rsplit("/", 2)[0])
from g3_cine_sweep import tribox

def main():
    a = sys.argv[1:]; kind, path, lo, hi = a[0], a[1], int(a[2]), int(a[3])
    X = float(a[a.index('--x') + 1]) if '--x' in a else 320.0
    W = int(a[a.index('--w') + 1]) if '--w' in a else 640
    retail = kind == 'retail'; H = 20 if retail else 16; lofs = 12 if retail else 8
    f = open(path, 'rb'); carry = b''; ci = 0; idx = 0; nfr = 0
    scis = collections.Counter(); tot = collections.Counter(); endx = collections.Counter(); stx = collections.Counter()
    fr_has = collections.Counter(); cur = collections.Counter(); scur = set(); curscis = None; anyc = False
    while idx < hi:
        h = f.read(H)
        if len(h) < H: break
        ln = struct.unpack_from('<I', h, lofs)[0]; buf = carry + f.read(ln); p = 0; n_ = len(buf)
        while p + 8 <= n_:
            w0, w1 = struct.unpack_from('<II', buf, p); op = (w0 >> 24) & 0x3F; n = 8
            live = lo <= idx < hi and ci == W
            if 0x08 <= op <= 0x0F or op in (0x24, 0x25, 0x36): anyc = True
            if 0x08 <= op <= 0x0F:
                n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
                if p + n > n_: break
                if live:
                    x0, x1, y0, y1 = tribox(buf, p)
                    if y1 > y0:
                        # clip the extent to the active scissor: edge-walker x values beyond it are not drawn
                        if curscis: x0, x1 = max(x0, curscis[0]), min(x1, curscis[2])
                        if x0 < X - 1 and x1 > X + 1: cur['straddle'] += 1
                        if X - 2 <= x1 <= X + 0.5: cur['endL'] += 1; endx[round(x1 * 4) / 4] += 1
                        if X - 0.5 <= x0 <= X + 2: cur['startR'] += 1; stx[round(x0 * 4) / 4] += 1
                        cur['tris'] += 1
            elif op in (0x24, 0x25, 0x36):
                n = 16 if op != 0x36 else 8
                if p + n > n_: break
                if live:
                    xl, xh = ((w1 >> 12) & 0xFFF) / 4, ((w0 >> 12) & 0xFFF) / 4
                    if abs(xl - X) <= 2 or abs(xh - X) <= 2: cur['rect@X'] += 1
                    cur['rects'] += 1
            elif op == 0x2D:
                curscis = (((w0 >> 12) & 0xFFF) / 4, (w0 & 0xFFF) / 4, ((w1 >> 12) & 0xFFF) / 4, (w1 & 0xFFF) / 4)
                if live: scur.add(curscis)
            elif op == 0x3F: ci = (w0 & 0x3FF) + 1
            elif op == 0x29:
                if lo <= idx < hi and cur:
                    nfr += 1; tot.update(cur)
                    for k in cur: fr_has[k] += 1
                    for s in scur: scis[s] += 1
                if anyc: idx += 1
                cur = collections.Counter(); scur = set(); anyc = False
            p += n
        carry = buf[p:]
    print('%s %s frames %d..%d: %d frames ci=%d' % (kind, path, lo, hi, nfr, W))
    print('  scissors (frames using):', ', '.join('%s:%d' % (s, c) for s, c in scis.most_common(6)))
    print('  totals:', dict(tot)); print('  frames with:', dict(fr_has))
    print('  endL x:', sorted(endx.items())[:12]); print('  startR x:', sorted(stx.items())[:12])

if __name__ == '__main__': main()
