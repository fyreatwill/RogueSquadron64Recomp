#!/usr/bin/env python3
"""s7826: path-aligned offset of moving texrect elements, retail rdplog vs port rdplog.

Moving HUD elements (the flight reticle) never match frame-for-frame between the arms (the s7821 rate split: port renders
more frames over the same motion), so the whole-frame and element scorers read them as misses. This tool aligns by PATH
instead of by frame: every retail position of an element (same w, h, PRIM) is measured against the polyline of the port
positions of that element. Same path at another sample phase -> distance ~0; a constant screen-space offset -> a constant
distance; a different path -> large. A planted shift of the retail track (--plant px, default 3) is the same-run positive
control: its median must come out ~= the planted shift.
Also prints, for every retail texrect element absent from the port window, which small shift (+-0.25/+-0.5 px in x or y)
makes it present (a one-signed class = systematic offset, scattered/none = animation).

usage: s7826_rect_path_offset.py RETAIL.bin[.zst] PORT.bin[.zst] --win r0:r1,p0:p1 [--elem W:H:PRIM ...] [--plant PX]
       default elements: the lvl1 flight reticle pair 51:59.5:00FF0064 and 25.5:29.75:00FF0064 (s7826).
"""
import sys, math, collections, importlib.util, os
HERE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('seg', os.path.join(HERE, 's7821_rdp_screen_segments.py'))
seg = importlib.util.module_from_spec(sp); sp.loader.exec_module(seg)

def rects(fr, a, b): return [set(k for k in c if k[0] != 'tri') for c, _ in fr[a:b]]

def track(rs, w, h, pr, dx=0.0):
    out = []
    for i, fs in enumerate(rs):
        ks = sorted(k for k in fs if k[4] == pr and abs(k[2] - k[0] - w) < .01 and abs(k[3] - k[1] - h) < .01)
        if ks: out.append((i, ks[0][0] + dx, ks[0][1]))
    return out

def segd(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)

def path_dist(rt, pt):
    if len(rt) < 1 or len(pt) < 2: return None
    ds = sorted(min(segd((x, y), pt[j][1:], pt[j + 1][1:]) for j in range(len(pt) - 1)) for _, x, y in rt)
    n = len(ds); return n, ds[n // 2], ds[int(n * .9)], ds[-1]

def main():
    a = sys.argv
    if len(a) < 4 or '--win' not in a: print(__doc__); return 2
    opt = lambda n, d: a[a.index(n) + 1] if n in a else d
    (r0, r1), (p0, p1) = [tuple(map(int, w.split(':'))) for w in opt('--win', '').split(',')]
    plant = float(opt('--plant', '3'))
    els = [a[i + 1] for i, x in enumerate(a) if x == '--elem'] or ['51:59.5:00FF0064', '25.5:29.75:00FF0064']
    R = rects(seg.frames(a[1], True), r0, r1); P = rects(seg.frames(a[2], False), p0, p1); pu = set().union(*P) if P else set()
    ok = True
    for e in els:
        w, h, pr = e.split(':'); w, h = float(w), float(h)
        rt, pt = track(R, w, h, pr), track(P, w, h, pr)
        d, c = path_dist(rt, pt), path_dist(track(R, w, h, pr, plant), pt)
        if not d: print(f'elem {e}: retail pts {len(rt)} port pts {len(pt)} -> not scorable'); ok = False; continue
        ps = set((x, y) for _, x, y in pt); cls = collections.Counter()
        for _, x, y in rt:
            cls[next((f'{dx:+g},{dy:+g}' for dx, dy in ((0, 0), (0, .5), (0, -.5), (.5, 0), (-.5, 0), (0, .25), (0, -.25), (.25, 0), (-.25, 0))
                      if (x + dx, y + dy) in ps), 'path-interp')] += 1
        print(f'elem {e}: retail pts {d[0]} port pts {len(pt)} path-dist median {d[1]:.2f} p90 {d[2]:.2f} max {d[3]:.2f} | '
              f'plant +{plant:g}px median {c[1]:.2f} ({"PASS" if abs(c[1] - plant) < 0.6 else "FAIL"}) | port-pos shift classes {dict(cls)}')
        ok &= abs(c[1] - plant) < 0.6
    cls = collections.Counter(); byp = collections.Counter(); tot = 0
    for fs in R:
        for k in fs:
            tot += 1
            if k in pu: cls['exact'] += 1; continue
            c = next((f'{dx:+g},{dy:+g}' for dx, dy in ((0, .5), (0, -.5), (.5, 0), (-.5, 0), (0, .25), (0, -.25), (.25, 0), (-.25, 0))
                      if (k[0] + dx, k[1] + dy, k[2] + dx, k[3] + dy, k[4]) in pu), 'none')
            cls[c] += 1; byp[(c, k[4])] += 1
    print(f'all retail texrect elements {tot}: shift classes vs port window {dict(cls)}')
    print('  top (class, PRIM):', [x for x in byp.most_common(6) if x[0][0] != 'none'][:4], '| none:', [x for x in byp.most_common(12) if x[0][0] == 'none'][:4])
    return 0 if ok else 1

if __name__ == '__main__': sys.exit(main())
