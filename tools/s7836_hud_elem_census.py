#!/usr/bin/env python3
"""s7836: per-capture census of the large flight-HUD texrect elements over a frame window, retail rdplog or port rdplog.
Prints, for each capture: the commonest positions of the flight reticle pair (51x59.5 'b' and 25.5x29.75 's', PRIM 00FF0064),
the 52x64 icon instances by (x, y, PRIM) and every >=40x40 element by (w, h, x, y). Use it when s7826_rect_path_offset.py
reports an element 'absent' or a constant path distance: a near-static element (the reticle at rest) makes the path scorer's
plant control weak (it FAILed retail-vs-retail on lvl3), while a direct position census answers 'same place or not' exactly.
An element present at the same (x, y) with a different PRIM is a colour STATE (e.g. the top-left shield icon), not a missing draw.
--control (s7950): same-run planted control on the FIRST capture: every element shifted +1 px in y must move the top reticle rest
positions (b and s) by exactly +1 px with the same counts, and an unshifted re-census must reproduce them; 'CONTROL PASS'/'FAIL' (rc 3).
Each capture also prints one 'REST <kind> b=(x,y)xN s=(x,y)xN' line (the s7951 gate-sweep row regexes it).
usage: s7836_hud_elem_census.py CAPTURE[.zst]:retail|port:F0:F1 [...] [--control]"""
import sys, os, collections, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('seg', os.path.join(HERE, 's7821_rdp_screen_segments.py'))
seg = importlib.util.module_from_spec(sp); sp.loader.exec_module(seg)

FR = {}
def census(path, isret, a, b, dy=0.0):
    if (path, isret) not in FR: FR[(path, isret)] = seg.frames(path, isret)
    fr = FR[(path, isret)][a:b]
    ret, big, icon = collections.Counter(), collections.Counter(), collections.Counter()
    for c, _ in fr:
        for k in c:
            if k[0] == 'tri': continue
            if dy: k = (k[0], k[1] + dy, k[2], k[3] + dy) + tuple(k[4:])
            w, h = k[2] - k[0], k[3] - k[1]
            if k[4] == '00FF0064' and abs(w - 25.5) < .01: ret[('s', k[0], k[1])] += 1
            if k[4] == '00FF0064' and abs(w - 51) < .01: ret[('b', k[0], k[1])] += 1
            if abs(w - 52) < .01 and abs(h - 64) < .01: icon[(k[0], k[1], k[4])] += 1
            if w >= 40 and h >= 40: big[(round(w, 2), round(h, 2), k[0], k[1])] += 1
    return len(fr), ret, icon, big

def rest(ret):
    top = {}
    for (kd, x, y), n in ret.most_common():
        top.setdefault(kd, ((x, y), n))
    return top

def main():
    ctl = '--control' in sys.argv
    specs = [x for x in sys.argv[1:] if x != '--control']
    if not specs or any(x.startswith('-') or x.count(':') < 3 for x in specs):
        print(__doc__); return 2  # input-needing report tool: 'usage: ' line -> gate sweep NEEDS-ARGS (s7836 fix)
    for spec in specs:
        path, kind, a, b = spec.rsplit(':', 3)
        n, ret, icon, big = census(path, kind == 'retail', int(a), int(b))
        t = rest(ret)
        print(f'REST {kind} ' + ' '.join(f'{kd}=({t[kd][0][0]},{t[kd][0][1]})x{t[kd][1]}' if kd in t else f'{kd}=none' for kd in 'bs'))
        print(f'== {path} [{a}:{b}] frames {n}')
        print('  reticle', ret.most_common(8))
        print('  52x64  ', icon.most_common(6))
        print('  >=40   ', big.most_common(8))
    if ctl:
        path, kind, a, b = specs[0].rsplit(':', 3)
        t0 = rest(census(path, kind == 'retail', int(a), int(b))[1])
        t1 = rest(census(path, kind == 'retail', int(a), int(b), dy=1.0)[1])
        ok = bool(t0) and set(t0) == set(t1) and all(t1[k][0] == (t0[k][0][0], t0[k][0][1] + 1.0) and t1[k][1] == t0[k][1] for k in t0)
        print(f'CONTROL {"PASS" if ok else "FAIL"} (+1 px y plant: {t0} -> {t1})')
        if not ok: return 3
    return 0

if __name__ == '__main__': sys.exit(main())
