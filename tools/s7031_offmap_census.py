#!/usr/bin/env python3
"""s7031: summarise the last [s7030]/[s7031] report per phase from a run log: cells/f, culled/f, off-map share overall and per depth band
(0-0.5, 0.5-1.0, >=1.0 fog end), ring distance outside the map edge (median, share <=2, <=8) for all off-map cells and for the 0.5-1.0 band.
Usage: s7031_offmap_census.py run.log"""
import sys, re
L30, L31 = {}, {}
for ln in open(sys.argv[1], errors='replace'):
    m = re.search(r'\[s7030\] t=\d+ ph=(\d) k=(\S+) frames=(\d+) cells/f=(\S+) cull/f=(\S+) F=\S+ fe=(\S+) hist/f=(\S+)', ln)
    if m: L30[int(m[1])] = m
    m = re.search(r'\[s7031\] t=\d+ ph=(\d) R=(-?\d+) dims=(\S+) win=(\S+) ocull/f=(\S+) off/f=(\S+) ring/f=(\S+) rband/f=(\S+)', ln)
    if m: L31[int(m[1])] = m
def v(s): return [float(x) for x in s.split(',')]
def ringstat(r):
    t = sum(r) or 1; c = 0; med = None
    for i, x in enumerate(r):
        c += x
        if med is None and c >= t / 2: med = i
    return med, sum(r[:3]) / t, sum(r[:9]) / t
for p in sorted(L30):
    a, b = L30[p], L31.get(p)
    h = v(a[7]); o = v(b[6]) if b else [0] * 20
    band = lambda xs, i, j: sum(xs[i:j])
    print('ph=%d k=%s R=%s frames=%s cells/f=%s fogcull/f=%s offcull/f=%s fe=%s dims=%s win=%s' % (p, a[2], b[2] if b else '?', a[3], a[4], a[5], b[5] if b else '?', a[6], b[3] if b else '?', b[4] if b else '?'))
    for nm, i, j in (('0-0.5', 0, 5), ('0.5-1.0', 5, 10), ('>=1.0', 10, 20), ('all', 0, 20)):
        H, O = band(h, i, j), band(o, i, j)
        print('   band %-7s cells/f %7.1f off-map %7.1f (%.0f%%)' % (nm, H, O, 100 * O / H if H else 0))
    if b:
        for nm, r in (('all off', v(b[7])), ('band .5-1', v(b[8]))):
            med, s2, s8 = ringstat(r); print('   ring %-9s median %s  <=2 %.0f%%  <=8 %.0f%%  hist %s' % (nm, med, 100 * s2, 100 * s8, ','.join('%.0f' % x for x in r)))
