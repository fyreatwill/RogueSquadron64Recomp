"""s6488: per flight fbdump, join terrain score with preceding tricnt (len,tri,other).
Usage: g1c_lowframe_tris.py <run_dir> [low_thresh=0.03]"""
import sys, os, re, statistics as st
d = sys.argv[1]; thr = float(sys.argv[2]) if len(sys.argv) > 2 else 0.03
def load(p):
    b = open(p, "rb").read(); h = b.split(b"\n", 4); w, hh = map(int, h[2].split()); return w, hh, h[4]
def terr(w, h, px):
    t = n = 0
    for y in range(int(h*.30), int(h*.80)):
        o = y*w*3
        for x in range(60, w-60, 2):
            r, g, b = px[o+x*3], px[o+x*3+1], px[o+x*3+2]; n += 1
            if r > b+8 or g > b+8: t += 1
    return t/n
last = {}; rows = []; acc = dict(len=0, tri=0, other=0, tasks=0)
for ln in open(os.path.join(d, "run.log"), errors="replace"):
    m = re.match(r"\[tricnt\] ord=\d+ len=(\d+) tri=(\d+) trect=\d+ frect=\d+ other=(\d+)", ln)
    if m:
        last = dict(len=int(m[1]), tri=int(m[2]), other=int(m[3]))
        acc['len'] += last['len']; acc['tri'] += last['tri']; acc['other'] += last['other']; acc['tasks'] += 1; continue
    m = re.match(r"\[fbdump\] n=(\d+) fb=(0x[0-9A-Fa-f]+) stride=512", ln)
    if m and int(m[2], 16) in (0x80656000, 0x806AB000) and last:
        p = os.path.join(d, "fbd", "fb_%07d_w512.ppm" % int(m[1]))
        if os.path.exists(p):
            w, h, px = load(p)
            if w == 512: rows.append((terr(w, h, px), dict(acc)))
    if ln.startswith("[fbdump]"): acc = dict(len=0, tri=0, other=0, tasks=0)
lo = [r for r in rows if r[0] < thr]; hi = [r for r in rows if r[0] >= thr]
print(d, "frames", len(rows), "low", len(lo), "high", len(hi))
for tag, S in (("low", lo), ("high", hi)):
    if not S: continue
    for k in ("len", "tri", "other", "tasks"):
        v = [r[1][k] for r in S]; print(" ", tag, k, "med", st.median(v), "min", min(v), "max", max(v))
