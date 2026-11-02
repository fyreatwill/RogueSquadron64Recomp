#!/usr/bin/env python3
"""s6804 G3: coarse timeline of a long RDP stream (retail rdplog or RS64_RDP_BIN_PORT), for locating a screen change
(death camera, failure/retry screens) inside minutes of flight before scoring it with g3_rdp_segcmp.py.

Bins the g3_rdp_segments frame cache into windows of --bin frames; per bin prints the frame range, texrect count mode
(and its share), median tris, distinct texrect PRIM colours, and a 'set id' that is equal for bins whose modal texrect
multiset (coords+PRIM) is identical, so the same static screen is recognisable across arms.
usage: g3_rdp_timeline.py BIN retail|port [--bin 60] [--from F] [--to F]
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(__file__)); import g3_rdp_segments as sg
def arg(a, k, d): return int(a[a.index(k) + 1]) if k in a else d
if __name__ == '__main__':
    a = sys.argv; F = sg.all_frames(a[1], a[2] == 'retail'); B = arg(a, '--bin', 60)
    lo, hi = arg(a, '--from', 0), arg(a, '--to', len(F)); ids = {}
    print('frames', len(F))
    for s in range(lo, hi, B):
        W = F[s:min(s + B, hi)]
        rc = collections.Counter(sum(v for k, v in c.items() if k[0] != 'tri') for c in W)
        tr = sorted(sum(v for k, v in c.items() if k[0] == 'tri') for c in W)
        sets = collections.Counter(frozenset((k, v) for k, v in c.items() if k[0] != 'tri') for c in W)
        st, sn = sets.most_common(1)[0]; sid = ids.setdefault(st, len(ids))
        prims = len({k[4] for c in W for k in c if k[0] != 'tri'})
        m, mn = rc.most_common(1)[0]
        print('%6d-%6d rects %4d (%3d%%) tris %6d prims %3d set#%d (%d%%)' % (s, s + len(W), m, 100 * mn // len(W),
              tr[len(tr) // 2], prims, sid, 100 * sn // len(W)))
