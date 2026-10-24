"""s6057 G1c: fold a ROGUESQ_DD_TOGGLE run. Pairs each dumped fb with the dd state (blk) active when its [fbhash #n] line
was logged (stderr order), drops frames within GUARD swaps of a transition, and compares terrain-pixel fraction between
blk=0 (dd1) and blk=1 (dd=m). Usage: g1c_ddtog_fold.py <run_dir> [min_swap]"""
import re, sys, os, statistics as st
d = sys.argv[1]; minn = int(sys.argv[2]) if len(sys.argv) > 2 else 4500; GUARD = 6
state = 0; ms = {}; seq = []
for line in open(os.path.join(d, "run.log"), errors="replace"):
    m = re.match(r"\[ddtog\] call=(\d+) blk=(\d) m=([\d.]+)", line)
    if m: state = int(m.group(2)); ms[state] = float(m.group(3)); seq.append(("T", None)); continue
    m = re.match(r"\[fbhash #(\d+)\]", line)
    if m: seq.append(("F", (int(m.group(1)), state)))
fr = {}; last_t = -999; trans = []
for i, (k, v) in enumerate(seq):
    pass
cur = None; per = {}
tn = []
prev = 0
for k, v in seq:
    if k == "F": prev = v[0]
    else: tn.append(prev)
import bisect
def near_trans(n):
    i = bisect.bisect_right(tn, n) - 1
    off = n - tn[i] if i >= 0 else 0
    return not (4 <= off <= 8)  # frames mid-block only (guards a 1-4 swap call->swap lag)
for k, v in seq:
    if k == "F" and v[0] >= minn and v[0] % 3 == 0 and not near_trans(v[0]): per[v[0]] = v[1]
def metric(path):
    b = open(path, "rb").read(); hdr = b.split(b"\n", 4); w, h = map(int, hdr[2].split()); px = hdr[4]
    t1 = t2 = 0; rows = range(int(h * 0.30), int(h * 0.80)); tot = 0
    for y in rows:
        o = y * w * 3
        for x in range(60, w - 60, 2):
            r, g, bl = px[o + x * 3], px[o + x * 3 + 1], px[o + x * 3 + 2]; tot += 1
            if r > bl + 8 or g > bl + 8: t1 += 1
            if g >= bl - 4 and min(r, g, bl) < 190: t2 += 1
    return t1 / tot, t2 / tot
res = {0: [], 1: []}
for n, s in sorted(per.items()):
    p = os.path.join(d, "fbd", "fb_%07d_w512.ppm" % n)
    if os.path.exists(p): res[s].append(metric(p))
print("m by state:", ms, "frames", {k: len(v) for k, v in res.items()})
for s in (0, 1):
    if res[s]:
        print("blk%d tight mean %.4f med %.4f | loose mean %.4f med %.4f" % (s, st.mean(a for a, _ in res[s]), st.median(a for a, _ in res[s]), st.mean(b for _, b in res[s]), st.median(b for _, b in res[s])))

# per-offset breakdown (offset = swaps since the block transition, any offset, not just mid-block)
if "--offsets" in sys.argv:
    import collections
    byoff = collections.defaultdict(list); st2 = 0; prevn = 0; sts = {}
    for k, v in seq:
        if k == "F": sts[v[0]] = v[1]
    for n in sorted(sts):
        if n < minn or n % 3: continue
        i = bisect.bisect_right(tn, n) - 1; off = n - tn[i]
        p = os.path.join(d, "fbd", "fb_%07d_w512.ppm" % n)
        if os.path.exists(p) and off < 12: byoff[(sts[n], off)].append(metric(p)[0])
    for key in sorted(byoff): print("blk%d off%2d n=%d tight mean %.4f" % (key[0], key[1], len(byoff[key]), st.mean(byoff[key])))

# HUD presence: red radar-ring pixels in the top-right box, mid-block frames only
if "--hud" in sys.argv:
    def hud(path):
        b = open(path, "rb").read(); hdr = b.split(b"\n", 4); w, h = map(int, hdr[2].split()); px = hdr[4]; c = 0
        for y in range(20, 150):
            for x in range(380, 490):
                o = (y * w + x) * 3
                if px[o] > 150 and px[o + 1] < 60 and px[o + 2] < 60: c += 1
        return c
    hs = {0: [], 1: []}
    for n, s in sorted(per.items()):
        p = os.path.join(d, "fbd", "fb_%07d_w512.ppm" % n)
        if os.path.exists(p): hs[s].append(hud(p))
    for s in (0, 1): print("blk%d HUD red px: median %d, frames with >=50 red px: %d/%d" % (s, st.median(hs[s]), sum(1 for v in hs[s] if v >= 50), len(hs[s])))
