#!/usr/bin/env python3
"""s6543: terrain fraction (tight/loose, as g1c_fixed_score.terr) of each w512 fb dump, binned by the cap in force
(last [capalt] swap=.. cap=.. line before its [fbdump] n= line). Usage: g1c_fbd_bycap.py run.log fbd_dir [min_n]"""
import re, sys, os, statistics as st, collections
log, d = sys.argv[1], sys.argv[2]; minn = int(sys.argv[3]) if len(sys.argv) > 3 else 600
def load(p):
    b = open(p, "rb").read(); h = b.split(b"\n", 4); w, hh = map(int, h[2].split()); return w, hh, h[4]
def terr(w, h, px):
    t1 = t2 = tot = 0
    for y in range(int(h*.30), int(h*.80)):
        o = y*w*3
        for x in range(60, w-60, 2):
            r, g, b = px[o+x*3], px[o+x*3+1], px[o+x*3+2]; tot += 1
            if r > b+8 or g > b+8: t1 += 1
            if g >= b-4 and min(r, g, b) < 190: t2 += 1
    return t1/tot, t2/tot
cur = None; tag = {}
for l in open(log, errors='replace'):
    m = re.match(r'\[capalt\] swap=\d+ cap=(-?\d+)', l)
    if m: cur = int(m.group(1)); continue
    m = re.match(r'\[fbdump\] n=(\d+)', l)
    if m and cur is not None: tag[int(m.group(1))] = cur
R = collections.defaultdict(list)
for n, c in sorted(tag.items()):
    p = os.path.join(d, f"fb_{n:07d}_w512.ppm")
    if n < minn or not os.path.exists(p): continue
    w, h, px = load(p)
    if w != 512 or len(px) < w*h*3: continue
    R[c].append(terr(w, h, px))
for c in sorted(R):
    t = [a for a, _ in R[c]]; l = [b for _, b in R[c]]
    print(f"cap={c:>4} n={len(t)} tight med={st.median(t):.3f} mean={st.mean(t):.3f} | loose med={st.median(l):.3f} mean={st.mean(l):.3f}")
