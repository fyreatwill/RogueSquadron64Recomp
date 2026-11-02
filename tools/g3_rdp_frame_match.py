#!/usr/bin/env python3
"""s6783 G3: per-frame RDP-stream match, retail (tools/oracle rdplog RS64_RDP_BIN) vs port (RS64_RDP_BIN_PORT).

A frame = commands between FULL_SYNCs. Its signature = multiset of texrects (xh,yh,xl,yl,PRIM) and tris (PRIM only;
tri edge coeffs are not compared, so 3D models count by number). Each of the last K retail frames is matched to the
closest of the last K port frames (multiset symmetric difference); exact = 0 difference. Control: the same retail
frames against a different screen's port frames (--ctl PORTBIN) must NOT match, else the signature cannot discriminate.
Window-independent: no pixel, colour-space or capture-phase terms, so slideshow backdrops (texture address not in the
signature) and pulsing highlights (paired by PRIM) do not count as differences.
usage: g3_rdp_frame_match.py RETAIL.bin PORT.bin [--ctl OTHER_PORT.bin] [--k 240]
"""
import struct, sys, collections
def records(path, retail):
    f = open(path, 'rb').read(); o = 0; H = 20 if retail else 16; out = []
    while o + H <= len(f):
        ln = struct.unpack_from('<I', f, o + (12 if retail else 8))[0]; o += H; out.append((o, ln)); o += ln
    return f, out
def frames(path, retail, k):
    f, recs = records(path, retail)
    # walk the tail only: enough records for ~k+10 frames (retail cxd4 delivers small DPC chunks, port one per submit)
    take = len(recs); fr = []; cur = []
    lo = recs[max(0, len(recs) - (3000 * k if retail else 6 * k))][0] - (20 if retail else 16)
    cat = b''.join(f[o:o + ln] for o, ln in recs if o >= lo); a = 0; prim = None
    w = lambda i: struct.unpack_from('<I', cat, i)[0]
    while a + 8 <= len(cat):
        w0, w1 = w(a), w(a + 4); op = (w0 >> 24) & 0x3F; n = 8
        if 0x08 <= op <= 0x0F: n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0); cur.append(('tri', prim))
        elif op in (0x24, 0x25): n = 16; cur.append((((w1 >> 12) & 0xFFF) / 4, (w1 & 0xFFF) / 4, ((w0 >> 12) & 0xFFF) / 4, (w0 & 0xFFF) / 4, prim))
        elif op == 0x3A: prim = '%08X' % w1
        elif op == 0x29:
            if cur: fr.append(collections.Counter(cur))
            cur = []
        a += n
    return fr[-k:]
def score(R, P):
    ds = [min(sum(((c - q) + (q - c)).values()) for q in P) for c in R]
    return sum(d == 0 for d in ds), len(ds), sorted(ds)[len(ds) // 2], max(ds)
if __name__ == '__main__':
    a = sys.argv; k = int(a[a.index('--k') + 1]) if '--k' in a else 240
    R = frames(a[1], True, k); P = frames(a[2], False, k)
    n = lambda F: collections.Counter(sum(F[0].values()) and len(list(f.elements())) for f in F).most_common(3)
    print('frames retail %d port %d | items/frame retail %s port %s' % (len(R), len(P), n(R), n(P)))
    e, t, md, mx = score(R, P); print('match: exact %d/%d  median diff %d  max diff %d' % (e, t, md, mx))
    if '--ctl' in a:
        C = frames(a[a.index('--ctl') + 1], False, k); e, t, md, mx = score(R, C)
        print('control: exact %d/%d  median diff %d  max diff %d' % (e, t, md, mx))
