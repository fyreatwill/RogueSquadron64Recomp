#!/usr/bin/env python3
"""s6801 G3: whole-stream RDP frame segmentation, so one paired run can score several screens (and a positive control)
instead of only the tail that g3_rdp_frame_match/g3_rdp_phase read.

Parses every frame (FULL_SYNC-delimited, same signature as g3_rdp_frame_match: texrect (xh,yh,xl,yl,PRIM) + tri PRIM),
caches them as <bin>.frames.pkl, and prints run-length segments of (texrect count, tri bucket of 100).
--slice A:B writes frames[A:B] to stdout-named pickle for g3_rdp_segcmp.
usage: g3_rdp_segments.py BIN retail|port [--min 20]
"""
import sys, os, pickle, struct, collections
sys.path.insert(0, os.path.dirname(__file__)); import g3_rdp_frame_match as m
def all_frames(path, retail):
    pk = path + '.frames.pkl'
    if os.path.exists(pk) and os.path.getmtime(pk) > os.path.getmtime(path): return pickle.load(open(pk, 'rb'))
    f, recs = m.records(path, retail); cat = b''.join(f[o:o + ln] for o, ln in recs); del f
    fr = []; cur = []; prim = None; a = 0; n_ = len(cat); u = struct.unpack_from
    while a + 8 <= n_:
        w0, w1 = u('<II', cat, a); w0 = int.from_bytes(cat[a:a + 4], 'little'); w1 = int.from_bytes(cat[a + 4:a + 8], 'little')
        op = (w0 >> 24) & 0x3F; n = 8
        if 0x08 <= op <= 0x0F: n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0); cur.append(('tri', prim))
        elif op in (0x24, 0x25): n = 16; cur.append((((w1 >> 12) & 0xFFF) / 4, (w1 & 0xFFF) / 4, ((w0 >> 12) & 0xFFF) / 4, (w0 & 0xFFF) / 4, prim))
        elif op == 0x3A: prim = '%08X' % w1
        elif op == 0x29:
            if cur: fr.append(collections.Counter(cur))
            cur = []
        a += n
    pickle.dump(fr, open(pk, 'wb')); return fr
def key(c):
    return (sum(v for k, v in c.items() if k[0] != 'tri'), sum(v for k, v in c.items() if k[0] == 'tri') // 100)
if __name__ == '__main__':
    a = sys.argv; F = all_frames(a[1], a[2] == 'retail'); mn = int(a[a.index('--min') + 1]) if '--min' in a else 20
    segs = []; s = 0
    for i in range(1, len(F) + 1):
        if i == len(F) or key(F[i])[0] != key(F[s])[0]:
            segs.append((s, i)); s = i
    print('frames', len(F))
    for s, e in segs:
        if e - s >= mn:
            t = sorted(key(F[j])[1] * 100 for j in range(s, e))
            print('%6d-%6d n=%5d rects=%4d tris(q50)=%5d' % (s, e, e - s, key(F[s])[0], t[len(t) // 2]))
