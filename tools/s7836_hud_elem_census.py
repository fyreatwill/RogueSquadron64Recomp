#!/usr/bin/env python3
"""s7836: per-capture census of the large flight-HUD texrect elements over a frame window, retail rdplog or port rdplog.
Prints, for each capture: the commonest positions of the flight reticle pair (51x59.5 'b' and 25.5x29.75 's', PRIM 00FF0064),
the 52x64 icon instances by (x, y, PRIM) and every >=40x40 element by (w, h, x, y). Use it when s7826_rect_path_offset.py
reports an element 'absent' or a constant path distance: a near-static element (the reticle at rest) makes the path scorer's
plant control weak (it FAILed retail-vs-retail on lvl3), while a direct position census answers 'same place or not' exactly.
An element present at the same (x, y) with a different PRIM is a colour STATE (e.g. the top-left shield icon), not a missing draw.
Usage: s7836_hud_elem_census.py CAPTURE[.zst]:retail|port:F0:F1 [...]"""
import sys, os, collections, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('seg', os.path.join(HERE, 's7821_rdp_screen_segments.py'))
seg = importlib.util.module_from_spec(sp); sp.loader.exec_module(seg)

def census(path, isret, a, b):
    fr = seg.frames(path, isret)[a:b]
    ret, big, icon = collections.Counter(), collections.Counter(), collections.Counter()
    for c, _ in fr:
        for k in c:
            if k[0] == 'tri': continue
            w, h = k[2] - k[0], k[3] - k[1]
            if k[4] == '00FF0064' and abs(w - 25.5) < .01: ret[('s', k[0], k[1])] += 1
            if k[4] == '00FF0064' and abs(w - 51) < .01: ret[('b', k[0], k[1])] += 1
            if abs(w - 52) < .01 and abs(h - 64) < .01: icon[(k[0], k[1], k[4])] += 1
            if w >= 40 and h >= 40: big[(round(w, 2), round(h, 2), k[0], k[1])] += 1
    return len(fr), ret, icon, big

def main():
    if len(sys.argv) < 2: print(__doc__); return 2
    for spec in sys.argv[1:]:
        path, kind, a, b = spec.rsplit(':', 3)
        n, ret, icon, big = census(path, kind == 'retail', int(a), int(b))
        print(f'== {path} [{a}:{b}] frames {n}')
        print('  reticle', ret.most_common(8))
        print('  52x64  ', icon.most_common(6))
        print('  >=40   ', big.most_common(8))
    return 0

if __name__ == '__main__': sys.exit(main())
