"""s6489: per flight fbdump window, join ground score with cell-gate deltas ([cellcum]) and summed tricnt.
Usage: g1c_cellpass_tris.py <run_dir> [low_thresh=0.03]. Cell columns: entries=sum(e0..e7), pass=e7."""
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
acc = dict(tri=0); prev = None; pending = None; rows = []
for ln in open(os.path.join(d, "run.log"), errors="replace"):
    m = re.match(r"\[tricnt\] ord=\d+ len=(\d+) tri=(\d+)", ln)
    if m: acc['tri'] += int(m[2]); continue
    m = re.match(r"\[fbdump\] n=(\d+) fb=(0x[0-9A-Fa-f]+) stride=512", ln)
    if m: pending = (int(m[1]), int(m[2], 16)); continue
    m = re.match(r"\[cellcum\] n=(\d+) e0=(\d+) e1=(\d+) e2=(\d+) e3=(\d+) e4=(\d+) e5=(\d+) e6=(\d+) e7pass=(\d+)", ln)
    if m and pending and pending[0] == int(m[1]):
        cur = [int(m[i]) for i in range(2, 10)]
        if pending[1] in (0x80620000, 0x80690000) and prev is not None:
            p = os.path.join(d, "fbd", "fb_%07d_w512.ppm" % pending[0])
            if os.path.exists(p):
                w, h, px = load(p)
                if w == 512:
                    dl = [a-b for a, b in zip(cur, prev)]
                    rows.append((terr(w, h, px), sum(dl), dl[7], dl[3], acc['tri']))
        prev = cur; acc = dict(tri=0)
lo = [r for r in rows if r[0] < thr]; hi = [r for r in rows if r[0] >= thr]
print(d, "frames", len(rows), "low", len(lo), "high", len(hi))
for tag, S in (("low", lo), ("high", hi)):
    if not S: continue
    for i, k in ((1, "entries"), (2, "pass"), (3, "e3_linkfail"), (4, "tris")):
        v = [r[i] for r in S]; print(" ", tag, k, "med", st.median(v), "min", min(v), "max", max(v))
    pc = [r[4]/r[2] for r in S if r[2]]
    if pc: print(" ", tag, "tris/passcell med", round(st.median(pc), 1))
