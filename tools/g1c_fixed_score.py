"""s6069 G1c: score fixed-dd fb dumps (no [ddtog] needed). Per run dir: terrain fraction (tight/loose, as g1c_ddtog_fold.metric)
and HUD radar-ring red-pixel presence, over fb_*_w512.ppm with n>=min_n and n%3==0. Cross-run: compare distributions, not frames.
Usage: g1c_fixed_score.py <fbd_dir> [min_n]"""
import sys, os, glob, re, statistics as st
d = sys.argv[1]; minn = int(sys.argv[2]) if len(sys.argv) > 2 else 4500
def load(p):
    b = open(p, "rb").read(); h = b.split(b"\n", 4); w, hh = map(int, h[2].split()); return w, hh, h[4]
def terr(w, h, px):
    t1 = t2 = tot = 0
    for y in range(int(h * .30), int(h * .80)):
        o = y * w * 3
        for x in range(60, w - 60, 2):
            r, g, b = px[o + x*3], px[o + x*3 + 1], px[o + x*3 + 2]; tot += 1
            if r > b + 8 or g > b + 8: t1 += 1
            if g >= b - 4 and min(r, g, b) < 190: t2 += 1
    return t1 / tot, t2 / tot
def hud(w, h, px):
    c = 0
    for y in range(20, 150):
        for x in range(380, 490):
            o = (y * w + x) * 3
            if px[o] > 150 and px[o+1] < 60 and px[o+2] < 60: c += 1
    return c
T = []; H = []
for p in sorted(glob.glob(os.path.join(d, "fb_*_w512.ppm"))):
    n = int(re.search(r"fb_(\d+)_", p).group(1))
    if n < minn or n % 3: continue
    w, h, px = load(p)
    if w != 512 or len(px) < w * h * 3: continue  # mixed-width / truncated frames (L10 fbd)
    T.append(terr(w, h, px)); H.append(hud(w, h, px))
if not T: print("no frames"); sys.exit(1)
q = lambda v, f: sorted(v)[int(len(v) * f)]
print("%s frames=%d tight med %.4f p10 %.4f p90 %.4f | loose med %.4f | HUD>=50red: %d/%d (med %d)" % (
    os.path.basename(os.path.dirname(d.rstrip('/'))), len(T), st.median(a for a, _ in T), q([a for a, _ in T], .1), q([a for a, _ in T], .9),
    st.median(b for _, b in T), sum(1 for v in H if v >= 50), len(H), st.median(H)))
