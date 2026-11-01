"""s6701 G1c phase 2: one table row per run dir (scratch/agent/m6/<tag>) for the dd step-up batch.
Columns: hold summary (alive / stalls / crashlines), mission-phase [g1b] cost (t >= tmin: tasks/s mean + p10,
share of seconds below 28 tasks/s, gfx task sd_wall mean ms and worst max, vi/s), [tricnt] p90 tri per gfx
task over the second half of the run, and the g1c_fixed_score terrain fraction (tight median) over fbd dumps.
Usage: g1c_phase2_fold.py <run_dir>... [--tmin S] [--minn N]"""
import sys, os, re, glob, statistics as st
sys.path.insert(0, os.path.dirname(__file__))
args = sys.argv[1:]; tmin = 100; minn = 3000
if "--tmin" in args: i = args.index("--tmin"); tmin = int(args[i + 1]); del args[i:i + 2]
if "--minn" in args: i = args.index("--minn"); minn = int(args[i + 1]); del args[i:i + 2]
G1B = re.compile(rb"^\[g1b\] t=(\d+) vi=(\d+) tasks=(\d+) sd_wall=([\d.]+)/(\d+)")
TRI = re.compile(rb"^\[tricnt\] ord=\d+ len=\d+ tri=(\d+)")


def terr(w, h, px):  # same metric as g1c_fixed_score.terr (tight)
    t1 = tot = 0
    for y in range(int(h * .30), int(h * .80)):
        o = y * w * 3
        for x in range(60, w - 60, 2):
            r, g, b = px[o + x * 3], px[o + x * 3 + 1], px[o + x * 3 + 2]; tot += 1
            if r > b + 8 or g > b + 8: t1 += 1
    return t1 / tot


def fold(d):
    summ = open(os.path.join(d, "summary")).read().strip() if os.path.exists(os.path.join(d, "summary")) else "no-summary"
    g = []; tri = []
    with open(os.path.join(d, "run.log"), "rb") as f:
        for ln in f:
            m = G1B.match(ln)
            if m:
                t, vi, tk, sdm, sdx = int(m[1]), int(m[2]), int(m[3]), float(m[4]), int(m[5])
                if t >= tmin: g.append((vi, tk, sdm, sdx))
                continue
            m = TRI.match(ln)
            if m and int(m[1]): tri.append(int(m[1]))
    T = []
    for p in sorted(glob.glob(os.path.join(d, "fbd", "fb_*_w512.ppm"))):
        n = int(re.search(r"fb_(\d+)_", p).group(1))
        if n < minn: continue
        b = open(p, "rb").read(); h = b.split(b"\n", 4); w, hh = map(int, h[2].split())
        if w == 512 and len(h[4]) >= w * hh * 3: T.append(terr(w, hh, h[4]))
    row = {"run": os.path.basename(d.rstrip("/")), "summary": summ}
    if g:
        tk = sorted(x[1] for x in g)
        row.update(n=len(g), vi=st.mean(x[0] for x in g), tasks=st.mean(tk), tasks_p10=tk[len(tk) // 10],
                   below28=sum(1 for v in tk if v < 28) / len(tk), gfx_ms=st.mean(x[2] for x in g), gfx_max=max(x[3] for x in g))
    if tri: h2 = sorted(tri[len(tri) // 2:]); row["tri_p90"] = h2[int(len(h2) * .9)]
    if T: row.update(frames=len(T), terr_med=st.median(T))
    return row


for d in args:
    r = fold(d)
    print("%-28s n=%-4s vi=%-5s tasks=%-5s p10=%-3s <28=%-5s gfx=%-5s max=%-4s tri_p90=%-6s terr=%s(%s fr)" % (
        r["run"], r.get("n", "-"), "%.1f" % r["vi"] if "vi" in r else "-", "%.1f" % r["tasks"] if "tasks" in r else "-",
        r.get("tasks_p10", "-"), "%.2f" % r["below28"] if "below28" in r else "-", "%.1f" % r["gfx_ms"] if "gfx_ms" in r else "-",
        r.get("gfx_max", "-"), r.get("tri_p90", "-"), "%.4f" % r["terr_med"] if "terr_med" in r else "-", r.get("frames", 0)))
    print("    " + r["summary"])
