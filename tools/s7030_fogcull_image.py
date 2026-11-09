#!/usr/bin/env python3
"""s7030: per-phase image effect of a ROGUESQ_DD_FOGCULL=tog3 run, from a g5b_capture raw (<QII mach,w,h + w*h RGB per frame).
Phase = (mach/24e6)%3 (k = a,b,c); frames at second phase 0.15-0.85 only, in-flight frames only (left edge not black).
Per phase: mean image on a 4x2 subsampled grid over rows [y0, y1). Prints mean |P_i - P_0| per sample (RGB L1/3) and an A/A floor
(P0 frames of even vs odd 3-s cycles), plus per phase the mean far silhouette: per column the topmost row whose L1 distance from
the column's row-y0 pixel exceeds 45 (terrain or fog slab against sky). Culling visible terrain moves it down (larger y).
Usage: s7030_fogcull_image.py raw [y0=16] [y1_frac=0.75] [step=1]  (pure python, no numpy)"""
import sys, struct
raw = sys.argv[1]; y0 = int(sys.argv[2]) if len(sys.argv) > 2 else 16; yf = float(sys.argv[3]) if len(sys.argv) > 3 else 0.75; step = int(sys.argv[4]) if len(sys.argv) > 4 else 1
f = open(raw, 'rb'); t, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3; n = f.seek(0, 2) // rec; y1 = int(h * yf)
XS = list(range(0, w, 4)); YS = list(range(y0, y1, 2)); NS = len(XS) * len(YS)
acc = {}; cnt = {}; sil = {}
for i in range(0, n, step):
    f.seek(i * rec); t, _, _ = struct.unpack('<QII', f.read(16)); b = f.read(w * h * 3)
    o = (h // 2 * w + 3) * 3
    if b[o] + b[o + 1] + b[o + 2] + b[o + 6] + b[o + 7] + b[o + 8] < 20: continue
    s = t / 24e6; ph = s % 1
    if not 0.15 <= ph <= 0.85: continue
    p = int(s) % 3; key = (p, int(s) // 3 % 2)
    a = acc.setdefault(key, [0] * (NS * 3)); cnt[key] = cnt.get(key, 0) + 1
    j = 0
    for y in YS:
        r = y * w * 3
        for x in XS:
            q = r + x * 3; a[j] += b[q]; a[j + 1] += b[q + 1]; a[j + 2] += b[q + 2]; j += 3
    tot = 0
    for x in XS:
        q0 = (y0 * w + x) * 3; c0 = b[q0:q0 + 3]; yy = y1
        for y in YS:
            q = (y * w + x) * 3
            if abs(b[q] - c0[0]) + abs(b[q + 1] - c0[1]) + abs(b[q + 2] - c0[2]) > 45: yy = y; break
        tot += yy
    sil.setdefault(p, []).append(tot / len(XS))
def mean(keys):
    c = sum(cnt.get(k, 0) for k in keys); m = [0.0] * (NS * 3)
    for k in keys:
        if k in acc:
            for j, v in enumerate(acc[k]): m[j] += v
    return [v / max(c, 1) for v in m], c
def mad(A, B): return sum(abs(x - y) for x, y in zip(A, B)) / len(A)
M = {p: mean([(p, 0), (p, 1)]) for p in range(3)}
print("frames per phase:", {p: M[p][1] for p in range(3)}, "w,h", w, h, "band", y0, y1)
aa = mad(mean([(0, 0)])[0], mean([(0, 1)])[0])
for p in (1, 2):
    A, B = M[p][0], M[0][0]; rows = []
    for ri, y in enumerate(YS):
        lo = ri * len(XS) * 3; rows.append((mad(A[lo:lo + len(XS) * 3], B[lo:lo + len(XS) * 3]), y))
    rows.sort(reverse=True)
    print("P%d-P0 mean|d| %.2f  (A/A P0 halves %.2f)  worst rows %s" % (p, mad(A, B), aa, [(y, round(d, 1)) for d, y in rows[:3]]))
    for half in (0, 1):
        print("   P%d cycle%d vs P0 cycle%d: %.2f" % (p, half, half, mad(mean([(p, half)])[0], mean([(0, half)])[0])))
for p in range(3):
    v = sil.get(p, []); mu = sum(v) / len(v) if v else -1
    sd = (sum((x - mu) ** 2 for x in v) / len(v)) ** 0.5 if v else -1
    print("P%d silhouette mean y %.2f (n=%d, sd %.2f, sem %.2f)" % (p, mu, len(v), sd, sd / max(len(v), 1) ** 0.5))
