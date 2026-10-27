"""s6469 G1c: join [fbdump] records to a flight window and score matched dd1/dd8 frames.
Window = every [fbdump] whose fb is in the comma list (default 0x80656000,0x806AB000, the flight buffers in both s6468p arms;
0x80790000 is the title/select-game menu, a false start in the first s6469 pass);
frames are paired by index from each arm's first window dump (phase-relative key, not dump ordinal).
Usage: g1c_fbdump_join.py <run_dir_a> <run_dir_b> [fb_hex=0x80790000]"""
import sys, os, re, statistics as st
sys.path.insert(0, os.path.dirname(__file__))
fbs = {int(x, 16) for x in (sys.argv[3] if len(sys.argv) > 3 else "0x80656000,0x806AB000").split(",")}
def window(d):
    out = []
    for ln in open(os.path.join(d, "run.log"), errors="replace"):
        m = re.match(r"\[fbdump\] n=(\d+) fb=(0x[0-9A-Fa-f]+) stride=(\d+)", ln)
        if not m: continue
        if int(m.group(2), 16) in fbs and m.group(3) == "512": out.append(int(m.group(1)))
    return out
def load(p):
    b = open(p, "rb").read(); h = b.split(b"\n", 4); w, hh = map(int, h[2].split()); return w, hh, h[4]
def terr(w, h, px):
    t1 = tot = 0
    for y in range(int(h*.30), int(h*.80)):
        o = y*w*3
        for x in range(60, w-60, 2):
            r, g, b = px[o+x*3], px[o+x*3+1], px[o+x*3+2]; tot += 1
            if r > b+8 or g > b+8: t1 += 1
    return t1/tot
def hud(w, h, px):
    c = 0
    for y in range(20, 150):
        for x in range(380, 490):
            o = (y*w+x)*3
            if px[o] > 150 and px[o+1] < 60 and px[o+2] < 60: c += 1
    return c
def score(d, ns):
    T = []; H = []
    for n in ns:
        p = os.path.join(d, "fbd", "fb_%07d_w512.ppm" % n)
        if not os.path.exists(p): continue
        w, h, px = load(p)
        if w != 512 or len(px) < w*h*3: continue
        T.append(terr(w, h, px)); H.append(hud(w, h, px))
    return T, H
A, B = sys.argv[1], sys.argv[2]
wa, wb = window(A), window(B); k = min(len(wa), len(wb))
print("window A=%d dumps (n %d-%d) B=%d dumps (n %d-%d) matched=%d" % (len(wa), wa[0], wa[-1], len(wb), wb[0], wb[-1], k))
assert k > 0, "no matched flight dumps"
# skip first 10% (settling) and score the common index window
lo = k // 10; ia, ib = wa[lo:k], wb[lo:k]
for tag, d, ns in (("A", A, ia), ("B", B, ib)):
    T, H = score(d, ns); q = lambda v, f: sorted(v)[int(len(v)*f)]
    print("%s %s frames=%d terrain med %.4f p10 %.4f p90 %.4f | HUD>=50red %d/%d med %d" % (
        tag, os.path.basename(d.rstrip('/')), len(T), st.median(T), q(T, .1), q(T, .9), sum(v >= 50 for v in H), len(H), st.median(H)))
print("matched pairs (idx: nA nB)", [(a, b) for a, b in list(zip(ia, ib))[::max(1, len(ia)//8)]])
