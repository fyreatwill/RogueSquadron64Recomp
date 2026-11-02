#!/usr/bin/env python3
"""s6799 G3: find long, sub-pixel-thin RDP triangles ("thin lines") in an RDP dump, port or retail.

Port dump  (RS64_RDP_BIN_PORT, 16-byte hdr 'PRDP',lo,len,stamp; stamp = VI with RS64_RDP_BIN_PORT_VI=1).
Retail dump (tools/oracle rdplog RS64_RDP_BIN, 20-byte hdr 'RDPC',origin,width,len,vi) -> --retail.
Each triangle's three vertices come from its edge coefficients (as rs64_spike_scan): A=(XH,YH), B=(XL,YM),
C=(XH+DxHDy*(YL-YH),YL). thickness = 2*area/longest edge; vis = length of the longest edge clipped to the
colour image width x scissor lry (flight is 512x448). A sliver = thickness < --thick (1.0 px)
and vis > --len (60 px). Per sliver: frame, stamp, vertices, texture image, combiner, othermode hi, prim colour.
Culled tris (rs64_spike_scan zeroes YL/YM/YH) are skipped and counted.
usage: g3_sliver_scan.py DUMP [--retail] [--thick 1.0] [--len 60] [--from STAMP] [--to STAMP] [--rows N]
"""
import struct, sys, collections, math, mmap

def arg(n, d):
    a = sys.argv
    return type(d)(a[a.index(n) + 1]) if n in a else d

def records(path, retail):
    fh = open(path, 'rb'); f = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ); o = 0; H = 20 if retail else 16
    while o + H <= len(f):
        ln = struct.unpack_from('<I', f, o + (12 if retail else 8))[0]
        st = struct.unpack_from('<I', f, o + (16 if retail else 12))[0]
        yield st, f[o + H:o + H + ln]; o += H + ln

def clip_len(p, q, w, h):
    # Liang-Barsky clip of segment p-q to [0,w]x[0,h]; returns visible length
    x0, y0 = p; dx, dy = q[0] - x0, q[1] - y0; t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, x0), (dx, w - x0), (-dy, y0), (dy, h - y0)):
        if pp == 0:
            if qq < 0: return 0.0
            continue
        r = qq / pp
        if pp < 0: t0 = max(t0, r)
        else: t1 = min(t1, r)
        if t0 > t1: return 0.0
    return (t1 - t0) * math.hypot(dx, dy)

def main():
    path = sys.argv[1]; retail = '--retail' in sys.argv
    TH, LN = arg('--thick', 1.0), arg('--len', 60.0); lo_st, hi_st = arg('--from', 0), arg('--to', 1 << 31)
    rows = arg('--rows', 60)
    s14 = lambda v: (((v & 0x3FFF) ^ 0x2000) - 0x2000) / 4.0
    s32 = lambda v: (v - (1 << 32) if v & 0x80000000 else v) / 65536.0
    frame = 0; ntri = 0; nculled = 0; cw = 320; sch = 240.0; timg = 0; comb = (0, 0); omh = 0; prim = 0
    FLAT = arg('--flat', 0.5); fl512 = {}; flat_by = collections.Counter(); flat_y = collections.Counter(); flat_ex = []; oml = 0
    slivers = []; per_frame = collections.Counter(); frame_st = {}; ftris = collections.Counter()
    buf = b''; cur_st = 0
    for st, data in records(path, retail):
        if st < lo_st or st > hi_st:
            continue
        # retail cxd4 delivers small DPC chunks that split commands: carry the unparsed tail into the next record
        data = buf + bytes(data); buf = b''
        cur_st = st; a = 0; n = len(data); w = lambda i: struct.unpack_from('<I', data, i)[0]
        while a + 8 <= n:
            w0, w1 = w(a), w(a + 4); op = (w0 >> 24) & 0x3F; ln = 8
            if 0x08 <= op <= 0x0F:
                ln = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
                if a + ln > n: break
                yl, ym, yh = s14(w0), s14(w1 >> 16), s14(w1)
                ntri += 1; ftris[frame] += 1
                if yl == 0 and ym == 0 and yh == 0:
                    nculled += 1
                else:
                    xl, dl, xh, dh, xm, dm = (s32(w(a + o)) for o in (8, 12, 16, 20, 24, 28))
                    A = (xh, yh); B = (xl, ym); C = (xh + dh * (yl - yh), yl)
                    e = [(A, B), (B, C), (C, A)]
                    L = [math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in e]
                    k = max(range(3), key=lambda i: L[i])
                    area2 = abs((B[0] - A[0]) * (C[1] - A[1]) - (C[0] - A[0]) * (B[1] - A[1]))
                    th = area2 / L[k] if L[k] > 0 else 0.0
                    if cw == 512:
                        fl512[frame] = fl512.get(frame, 0)
                        if yl - yh <= FLAT and max(A[0], B[0], C[0]) - min(A[0], B[0], C[0]) > 30:
                            fl512[frame] += 1; flat_by[comb] += 1; flat_y[round(yh)] += 1
                            if len(flat_ex) < 6: flat_ex.append((cur_st, A, B, C, comb, omh, oml))
                    if th < TH and L[k] > LN:
                        vis = clip_len(e[k][0], e[k][1], float(cw), sch)
                        if vis > LN:
                            slivers.append((frame, cur_st, op, A, B, C, th, vis, L[k], timg, comb, omh, prim, cw))
                            per_frame[frame] += 1
            elif op in (0x24, 0x25):
                ln = 16
                if a + ln > n: break
            elif op == 0x3F: cw = (w0 & 0x3FF) + 1
            elif op == 0x2D: sch = (w1 & 0xFFF) / 4.0
            elif op == 0x3D: timg = w1 & 0xFFFFFF
            elif op == 0x3C: comb = (w0 & 0xFFFFFF, w1)
            elif op == 0x2F: omh = w0 & 0xFFFFFF; oml = w1
            elif op == 0x3A: prim = w1
            elif op == 0x29:
                frame_st[frame] = cur_st; frame += 1
            a += ln
        buf = data[a:]
    frame_st.setdefault(frame, cur_st)
    print('frames %d tris %d culled(zeroed) %d slivers %d in %d frames (thick<%.2f vis>%.0f)' % (
        frame, ntri, nculled, len(slivers), len(per_frame), TH, LN))
    nf = len(fl512); nfl = sum(1 for v in fl512.values() if v)
    print('flat tris (height <= %.2f px, width > 30 px) in 512-wide frames: %d/%d frames (%.1f%%), %d tris, %.2f/frame' % (
        FLAT, nfl, nf, 100.0 * nfl / max(nf, 1), sum(fl512.values()), sum(fl512.values()) / max(nf, 1)))
    for c, m_ in flat_by.most_common(5): print('  comb %06X:%08X n=%d' % (c[0], c[1], m_))
    print('  yh histogram (top):', flat_y.most_common(8))
    for e_ in flat_ex: print('  ex st%d A(%.2f,%.2f) B(%.2f,%.2f) C(%.2f,%.2f) comb=%06X:%08X om=%06X:%08X' % (e_[0], *e_[1], *e_[2], *e_[3], *e_[4], e_[5], e_[6]))
    byt = collections.Counter((s[9], s[10]) for s in slivers)
    print('by texture/combiner:')
    for (t, c), m in byt.most_common(12):
        print('  timg %06X comb %06X:%08X  n=%d frames=%d' % (t, c[0], c[1], m, len({s[0] for s in slivers if s[9] == t and s[10] == c})))
    # runs of consecutive frames carrying slivers
    fr = sorted(per_frame); runs = []; s0 = p = None
    for f in fr:
        if s0 is None: s0 = p = f
        elif f <= p + 2: p = f
        else: runs.append((s0, p)); s0 = p = f
    if s0 is not None: runs.append((s0, p))
    runs.sort(key=lambda r: -(r[1] - r[0]))
    print('longest sliver runs (frames, stamp range, n slivers):')
    for r in runs[:12]:
        print('  f%d-%d st %d-%d  n=%d' % (r[0], r[1], frame_st.get(r[0], 0), frame_st.get(r[1], 0), sum(per_frame[f] for f in range(r[0], r[1] + 1))))
    print('sample rows:')
    for s in slivers[:rows]:
        f, st, op, A, B, C, th, vis, L, t, c, om, pr, w_ = s
        print('  f%d st%d op%02X A(%.1f,%.1f) B(%.1f,%.1f) C(%.1f,%.1f) th=%.3f vis=%.0f len=%.0f timg=%06X comb=%06X:%08X om=%06X prim=%08X cw=%d' % (
            f, st, op, A[0], A[1], B[0], B[1], C[0], C[1], th, vis, L, t, c[0], c[1], om, pr, w_))

if __name__ == '__main__':
    main()
