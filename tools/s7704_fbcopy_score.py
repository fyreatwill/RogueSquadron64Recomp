#!/usr/bin/env python3
"""s7704: score g5b_capture raws of the boot cinematic arms (tools/s7704_wide_fbcopy_arms.zsh). PIL only (no numpy on this host).
timeline: per 1 s bin (from the first frame) mean luminance per arm, and content onset (first frame with mean luma > ON after t>1 s).
diff: align B to A on content onset; for each A frame in [t0,t1] (s after A onset) the best-match mean abs diff (0..255, frames reduced 2x)
to any B frame within +-W ms of the same onset-relative time. Per 0.5 s bin p50/max, A's own frame-to-frame diff (motion scale), and the
mean best diff per 8 column bands (where on screen a difference sits).
usage: s7704_fbcopy_score.py timeline a.raw [b.raw ...] | diff a.raw b.raw t0 t1 [W_ms=120] [ON=8]"""
import sys, struct, os
from PIL import Image, ImageChops, ImageStat
def load(p):
    f = open(p, 'rb'); b, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w*h*3; n = os.path.getsize(p)//rec
    T = []
    for i in range(n): f.seek(i*rec); T.append((struct.unpack('<Q', f.read(8))[0]-b)/24e6)
    def fr(i): f.seek(i*rec+16); return Image.frombytes('RGB', (w, h), f.read(w*h*3)).reduce(2)
    return T, fr, w, h
def luma(im): return sum(ImageStat.Stat(im.reduce(4)).mean)/3
def onset(T, fr, ON):
    for i, t in enumerate(T):
        if t > 1.0 and luma(fr(i)) > ON: return t
    return 0.0
def mad(x, y): return sum(ImageStat.Stat(ImageChops.difference(x, y)).mean)/3
mode = sys.argv[1]
if mode == 'timeline':
    for p in sys.argv[2:]:
        T, fr, w, h = load(p); on = onset(T, fr, 8); out = []; b = 0.0; i = 0
        while b < T[-1]:
            js = [j for j in range(i, len(T)) if b <= T[j] < b+1][::10]
            out.append(f'{b:.0f}:{sum(luma(fr(j)) for j in js)/len(js):.0f}' if js else f'{b:.0f}:-'); b += 1
        print(p.split('/')[-1], f'{w}x{h} n={len(T)} onset={on:.2f}s'); print('  ', ' '.join(out))
else:
    a, bb, t0, t1 = sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5])
    W = float(sys.argv[6])/1e3 if len(sys.argv) > 6 else 0.12; ON = float(sys.argv[7]) if len(sys.argv) > 7 else 8
    TA, FA, w, h = load(a); TB, FB, w2, h2 = load(bb)
    if (w, h) != (w2, h2): sys.exit('size mismatch')
    oa = onset(TA, FA, ON); ob = onset(TB, FB, ON); RA = [t-oa for t in TA]; RB = [t-ob for t in TB]
    print(f'{a.split("/")[-1]} onset {oa:.2f}  vs  {bb.split("/")[-1]} onset {ob:.2f}')
    bins = {}; prevd = []; nb = 8; band = [0.0]*nb; nband = 0; prev = None; cache = {}
    def gb(j):
        if j not in cache: cache[j] = FB(j)
        return cache[j]
    for i, r in enumerate(RA):
        if not (t0 <= r <= t1): continue
        x = FA(i); js = [j for j, s in enumerate(RB) if abs(s-r) <= W]
        best = min(((mad(x, gb(j)), j) for j in js), default=(float('nan'), -1))
        bins.setdefault(int((r-t0)*2), []).append(best[0])
        if best[1] >= 0:
            d = ImageChops.difference(x, gb(best[1])); bw = d.size[0]//nb
            for k in range(nb): band[k] += sum(ImageStat.Stat(d.crop((k*bw, 0, (k+1)*bw, d.size[1]))).mean)/3
            nband += 1
        if prev is not None: prevd.append(mad(x, prev))
        prev = x
        if len(cache) > 400: cache.clear()
    for k in sorted(bins):
        v = sorted(bins[k]); print(f'  t {t0+k/2:5.1f}: n={len(v):3d} bestdiff p50 {v[len(v)//2]:6.2f} max {v[-1]:6.2f}')
    pd = sorted(prevd); print(f'  A self frame-to-frame diff p50 {pd[len(pd)//2]:.2f} p90 {pd[len(pd)*9//10]:.2f} (motion scale)')
    print('  column bands L->R mean bestdiff:', ' '.join(f'{v/max(nband,1):.2f}' for v in band))
