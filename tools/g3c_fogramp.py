#!/usr/bin/env python3
"""s6304 G3c(a): where does forced magenta fog land? Usage: g3c_fogramp.py <fbd-dir> [min-frame] [stride]
Per frame, terrain rows = rows 15%..85% containing any non-sky terrain pixel (r>b+8 or g>b+8, or magenta).
Splits those rows into thirds (far=top, mid, near=bottom) and reports mean magenta fraction (r>180,b>180,g<90)
among non-sky pixels in each third. Control: magenta total must be >0 in a fog arm and ~0 in the nofog arm.
Outcome A (far third magenta ~ low while near/mid high) = ramp ends short of far edge (H-fade selected);
B (far third heavily magenta) = haze reaches the edge, H-fade refuted.
"""
import glob, statistics, sys

def load(p):
    d = open(p, "rb").read().split(b"\n", 4)
    w, h = map(int, d[2].split()); return w, h, d[4]

def main():
    dr = sys.argv[1]; mn = int(sys.argv[2]) if len(sys.argv) > 2 else 0; st = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    fs = sorted(glob.glob(dr + "/*.ppm"))[mn::st]
    thirds = [[], [], []]; tot = 0
    for f in fs:
        w, h, px = load(f)
        rows = []
        for y in range(int(h*.15), int(h*.85)):
            n = m = 0
            for x in range(0, w, 4):
                o = (y*w+x)*3; r, g, b = px[o], px[o+1], px[o+2]
                mag = r > 180 and b > 180 and g < 90
                if mag or r > b+8 or g > b+8:
                    n += 1; m += mag
            if n: rows.append((m, n))
        if len(rows) < 6: continue
        k = len(rows)//3
        for i in range(3):
            seg = rows[i*k:(i+1)*k if i < 2 else len(rows)]
            thirds[i].append(sum(a for a, _ in seg)/max(1, sum(b for _, b in seg)))
        tot += sum(a for a, _ in rows)
    print(f"{dr}: frames={len(thirds[0])} magenta_px_total={tot}")
    for name, t in zip(("far", "mid", "near"), thirds):
        print(f"  {name}: mean={statistics.mean(t) if t else float('nan'):.4f}")
main()
