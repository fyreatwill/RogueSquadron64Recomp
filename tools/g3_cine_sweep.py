#!/usr/bin/env python3
"""s6792 G3 cinematic sweep: stream-summarise a retail (rdplog RS64_RDP_BIN) or port (RS64_RDP_BIN_PORT) RDP dump
into one row per frame (FULL_SYNC-delimited), without loading the multi-GB file.

  g3_cine_sweep.py summ  retail|port DUMP.bin OUT.tsv
      row: idx  ci_width  tris  texrects  fillrects  sig   (sig = hash of the g3_rdp_frame_match signature:
      texrects (xh,yh,xl,yl,PRIM) + PRIM-tagged tris)
  g3_cine_sweep.py summ ... --edge LO:HI:XMIN   (frames LO..HI-1 only, + OUT.edge: tris/rects wholly right of XMIN)
  g3_cine_sweep.py sweep RETAIL.tsv PORT.tsv [--w 640] [--rlog ORACLE.log]
      --rblock/--pblock START:LEN pick the playlist rows; --rt0 T = the retail vi-poll run starting at >= T s
      --rlog: retail per-shot seconds from the oracle's --vi-poll swaps; port seconds need RS64_RDP_BIN_PORT_VI=1
      (s6792) per-shot seconds + a time-aligned tri cost with a cross-shot control; see the printed legend.
      takes the last contiguous run of --w-wide frames (the playlist), splits it into shots at the game's 3-frame blank
      cuts (0 tris, <= 1 texrect), pairs shot k with shot k, and reports per shot: frame counts, tri medians, exact
      signature / tri-count % (frame i vs i), tri-series correlation after stretching the port shot to the retail length,
      and a CONTROL = the best correlation of the same retail shot against any OTHER port shot. H-match: corr >> control.
"""
import struct, sys, hashlib, collections, statistics as st

def tribox(buf, a):
    """x extent (pixels) of an RDP edge-walker triangle at buf[a]: the three edges' x at their start and end y"""
    w = struct.unpack_from('<8I', buf, a); sx = lambda v: (v - (1 << 32) if v & 0x80000000 else v) / 65536.0
    sy = lambda v: (v - (1 << 14) if v & 0x2000 else v) / 4.0
    yl, ym, yh = sy(w[0] & 0x3FFF), sy((w[1] >> 16) & 0x3FFF), sy(w[1] & 0x3FFF)
    xl, dl, xh, dh, xm, dm = sx(w[2]), sx(w[3]), sx(w[4]), sx(w[5]), sx(w[6]), sx(w[7])
    xs = (xh, xh + dh * (yl - yh), xm, xm + dm * (ym - yh), xl, xl + dl * (yl - ym))
    return min(xs), max(xs), yh, yl

def summ(kind, path, out, edge=None):
    """edge = (lo, hi, xmin): for frames lo..hi-1 also write OUT.edge rows: idx, tris whose whole x extent is >= xmin
    (with PRIM and y range), and rects (texrect/fillrect) starting at x >= xmin"""
    retail = kind == 'retail'; H = 20 if retail else 16; lo = 12 if retail else 8
    eo = open(out + '.edge', 'w') if edge else None; eitems = []
    f = open(path, 'rb'); o = open(out, 'w'); carry = b''; prim = None; ci = 0; cur = []; idx = 0
    tri = trc = fil = 0
    while True:
        h = f.read(H)
        if len(h) < H: break
        ln = struct.unpack_from('<I', h, lo)[0]; stamp = struct.unpack_from('<I', h, H - 4)[0]
        buf = carry + f.read(ln); a = 0; n_ = len(buf)
        while a + 8 <= n_:
            w0, w1 = struct.unpack_from('<II', buf, a); op = (w0 >> 24) & 0x3F; n = 8
            if 0x08 <= op <= 0x0F:
                n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
                if a + n > n_: break
                cur.append(('tri', prim)); tri += 1
                if edge and edge[0] <= idx < edge[1]:
                    x0, x1, y0, y1 = tribox(buf, a)
                    if x0 >= edge[2]: eitems.append('T%08X:%.0f-%.0f:%.0f-%.0f' % (prim or 0, x0, x1, y0, y1))
            elif op in (0x24, 0x25):
                n = 16
                if a + n > n_: break
                cur.append((((w1 >> 12) & 0xFFF), (w1 & 0xFFF), ((w0 >> 12) & 0xFFF), (w0 & 0xFFF), prim)); trc += 1
                if edge and edge[0] <= idx < edge[1] and ((w1 >> 12) & 0xFFF) / 4 >= edge[2]:
                    eitems.append('R%08X:%d,%d-%d,%d' % (prim or 0, ((w1 >> 12) & 0xFFF) // 4, (w1 & 0xFFF) // 4, ((w0 >> 12) & 0xFFF) // 4, (w0 & 0xFFF) // 4))
            elif op == 0x36:
                fil += 1
                if edge and edge[0] <= idx < edge[1] and ((w1 >> 12) & 0xFFF) / 4 >= edge[2]:
                    eitems.append('F:%d,%d-%d,%d' % (((w1 >> 12) & 0xFFF) // 4, (w1 & 0xFFF) // 4, ((w0 >> 12) & 0xFFF) // 4, (w0 & 0xFFF) // 4))
            elif op == 0x3A: prim = w1
            elif op == 0x3F: ci = (w0 & 0x3FF) + 1
            elif op == 0x29:
                if cur or tri or trc or fil:
                    sig = hashlib.md5(repr(sorted(collections.Counter(cur).items(), key=repr)).encode()).hexdigest()[:12]
                    o.write('%d\t%d\t%d\t%d\t%d\t%s\t%d\n' % (idx, ci, tri, trc, fil, sig, stamp))
                    if eo and edge[0] <= idx < edge[1]: eo.write('%d\t%s\n' % (idx, ' '.join(eitems)))
                    idx += 1
                    if edge and idx >= edge[1]: break
                cur = []; tri = trc = fil = 0; eitems = []
            a += n
        carry = buf[a:]
        if edge and idx >= edge[1]: break
    o.close(); print(path, 'frames', idx)

def block(p, w, sel=None):
    """the LAST contiguous run of frames whose colour image is w wide (the AT THE MOVIES playlist; the boot cinematic
    is an earlier run), as (tris, texrects, sig) rows"""
    R = [l.rstrip('\n').split('\t') for l in open(p)]; runs = []; s = None
    for i, r in enumerate(R + [['', '0']]):
        if r[1] == str(w):
            if s is None: s = i
        elif s is not None: runs.append((s, i)); s = None
    a, b = runs[-1]
    if sel: a, b = sel[0], sel[0] + sel[1]  # explicit START:LEN (frame rows) when the dump holds several 640 blocks
    return [(int(r[2]), int(r[3]), r[5], int(r[6]) if len(r) > 6 else 0) for r in R[a:b]]

def retail_swaps(log, w, t0=None):
    """emulated time of each framebuffer swap in the oracle's last --vi-poll run of width w. Hi-res cinematics are
    interlaced: the origin flips by one 640-px line (0x500) every field, so a swap = any other origin change. s6792:
    swaps map 1:1 to rdplog frames in the playlist block (2448 swaps / 2447 frames, dir3)."""
    import re
    P = [(float(re.search(r't=\s*([\d.]+)', l).group(1)), re.search(r'[-=]> (\d+)', l).group(1), int(l.split('origin=')[1], 16))
         for l in open(log) if l.startswith('[vi-poll]')]
    i = len(P) - 1
    while i > 0 and P[i - 1][1] == str(w): i -= 1
    if t0 is not None:  # the width-w run that starts at emulated time >= t0
        i = next(k for k in range(len(P)) if P[k][0] >= t0 and P[k][1] == str(w) and (k == 0 or P[k - 1][1] != str(w)))
    j = i
    while j < len(P) and P[j][1] == str(w): j += 1
    B = P[i:j]
    return [B[0][0]] + [b[0] for a, b in zip(B, B[1:]) if abs(b[2] - a[2]) != 0x500 * w // 640]

def shots(F):
    """shots = maximal non-blank runs; the game separates cutscene shots with 3 frames of 0 tris"""
    out = []; s = None
    for i, (t, x, _, _) in enumerate(F + [(0, 0, '', 0)]):
        if t == 0 and x <= 1:
            if s is not None and i - s >= 10: out.append((s, i))
            s = None
        elif s is None: s = i
    return out

def corr(a, b):
    ma, mb = st.mean(a), st.mean(b); va = sum((x - ma) ** 2 for x in a) ** .5; vb = sum((y - mb) ** 2 for y in b) ** .5
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (va * vb) if va and vb else 0.0

def stretch(a, n):
    return [a[min(len(a) - 1, int(i * len(a) / n))] for i in range(n)]

def series(F, ts, hz=10):
    """tri count resampled on a time grid (hz) from per-frame times ts (frame held until the next one)"""
    out = []; k = 0; t0 = ts[0]; n = int((ts[-1] - t0) * hz)
    for g in range(n):
        t = t0 + g / hz
        while k + 1 < len(ts) and ts[k + 1] <= t: k += 1
        out.append(F[k][0])
    return out

def tcost(a, b):
    n = min(len(a), len(b))
    if n < 0.8 * max(len(a), len(b)) or n < 5: return float('nan')
    m = max(1.0, st.mean(a[:n]))
    return sum(abs(x - y) for x, y in zip(a[:n], b[:n])) / n / m

def sweep(rp, pp, w, rlog=None, rsel=None, psel=None, t0=None):
    R = block(rp, w, rsel); P = block(pp, w, psel); RS = shots(R); PS = shots(P)
    sw = retail_swaps(rlog, w, t0) if rlog else None
    if sw: print('retail swaps in the vi-poll run: %d over %.1f s (frames in block %d)' % (len(sw), sw[-1] - sw[0], len(R)))
    pt = [f[3] / 60.0 for f in P] if P[0][3] else None
    print('playlist block (ci width %d): retail %d frames / %d shots, port %d frames / %d shots' % (w, len(R), len(RS), len(P), len(PS)))
    print('time axis: retail = oracle vi-poll swaps, port = RDP dump VI stamp / 60; tcost = mean |dtri| / mean tri on a 10 Hz grid;'
          ' ctl = min tcost of this retail shot vs any OTHER port shot; FLAG when tcost >= ctl/2, |dsec| > 0.3 s or tri medians differ > 5%')
    print('shot r_len p_len  r_sec  p_sec  r_fps  p_fps r_tri p_tri tcost   ctl  corr_str exact_sig% flag')
    rows = []
    for k in range(min(len(RS), len(PS))):
        Ra = R[slice(*RS[k])]; Pa = P[slice(*PS[k])]; n = min(len(Ra), len(Pa))
        es = sum(Ra[i][2] == Pa[i][2] for i in range(n))
        rt = [f[0] for f in Ra]; c = corr(rt, stretch([f[0] for f in Pa], len(Ra)))
        rsec = psec = tc = ctl = float('nan')
        if sw and pt and RS[k][1] < len(sw):
            rts = sw[RS[k][0]:RS[k][1] + 1]; pts = pt[PS[k][0]:PS[k][1]] + [pt[PS[k][1] - 1] + 1 / 60.0]
            rsec, psec = rts[-1] - rts[0], pts[-1] - pts[0]
            ra = series(Ra + [Ra[-1]], rts); pa = series(Pa + [Pa[-1]], pts); tc = tcost(ra, pa)
            cs = []
            for j in range(len(PS)):
                if j == k or PS[j][1] - PS[j][0] < 10: continue
                pj = pt[PS[j][0]:PS[j][1]] + [pt[PS[j][1] - 1] + 1 / 60.0]
                x = tcost(ra, series(P[slice(*PS[j])] + [P[PS[j][1] - 1]], pj))
                if x == x: cs.append(x)
            ctl = min(cs) if cs else float('nan')
        rm, pm = st.median(rt), st.median(f[0] for f in Pa)
        fl = []
        if tc == tc and ctl == ctl and tc >= ctl / 2: fl.append('TCOST')
        if rsec == rsec and abs(rsec - psec) > 0.3: fl.append('DUR')
        if abs(pm - rm) > 0.05 * max(rm, 1): fl.append('TRI')
        rows.append((k, len(Ra), len(Pa), rsec, psec, tc, ctl, fl))
        print('%4d %5d %5d %6.1f %6.1f %6.1f %6.1f %5d %5d %5.3f %5.3f %8.3f %10.1f %s' % (k, len(Ra), len(Pa), rsec, psec,
              len(Ra) / rsec if rsec else 0, len(Pa) / psec if psec else 0, rm, pm, tc, ctl, c, 100 * es / n, ' '.join(fl)))
    if len(RS) != len(PS): print('SHOT COUNT DIFFERS: retail tail', RS[len(PS):], 'port tail', PS[len(RS):])
    return rows

if __name__ == '__main__':
    a = sys.argv
    if a[1] == 'summ': summ(a[2], a[3], a[4], tuple(map(float, a[a.index('--edge') + 1].split(':'))) if '--edge' in a else None)
    else:
        g = lambda k: a[a.index(k) + 1] if k in a else None; sel = lambda v: tuple(map(int, v.split(':'))) if v else None
        sweep(a[2], a[3], int(g('--w') or 640), g('--rlog'), sel(g('--rblock')), sel(g('--pblock')), float(g('--rt0')) if g('--rt0') else None)
