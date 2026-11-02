# s6785: phase-free hangar compare. Per frame: total tris, tri PRIM count, texrect count, the hologram tile grid
# (texrects with x0 in {110..111} = left column) y0/height/PRIM, and the PRIM-free texrect geometry multiset.
import sys, collections, statistics as st
sys.path.insert(0, 'tools'); import g3_rdp_frame_match as m
def feat(F):
    out = []
    for c in F:
        tris = sum(v for k, v in c.items() if k[0] == 'tri'); tp = len([k for k in c if k[0] == 'tri'])
        tx = [(k, v) for k, v in c.items() if k[0] != 'tri']
        holo = sorted((k[1], k[3] - k[1], k[4]) for k, v in tx if 110 <= k[0] < 111.5)
        geo = collections.Counter(); [geo.update({k[:4]: v}) for k, v in tx]
        out.append((tris, tp, sum(v for _, v in tx), holo, geo))
    return out
R = feat(m.frames(sys.argv[1], True, 240)); P = feat(m.frames(sys.argv[2], False, 240))
for tag, F in (('retail', R), ('port', P)):
    t = [f[0] for f in F]; print(tag, 'frames', len(F), 'tris min/med/max', min(t), st.median(t), max(t),
        'triPRIMs', collections.Counter(f[1] for f in F).most_common(3), 'texrects', collections.Counter(f[2] for f in F).most_common(3))
    hy = collections.Counter((h[0][0], h[0][1]) if h else None for h in (f[3] for f in F))
    print('  holo left-col first tile (y0,h):', len(hy), 'distinct; top', hy.most_common(6))
    print('  holo rows/frame', collections.Counter(len(f[3]) for f in F).most_common(4))
ry = set(); py = set()
for f in R: ry |= {(a, b) for a, b, _ in f[3]}
for f in P: py |= {(a, b) for a, b, _ in f[3]}
print('holo (y0,h) retail-only', len(ry - py), 'port-only', len(py - ry), 'shared', len(ry & py))
# geometry-only best-pair diff, excluding the hologram grid
def strip(g): return collections.Counter({k: v for k, v in g.items() if not (110 <= k[0] <= 401 and 20 <= k[1] <= 160)})
ds = [min(sum(((strip(r[4]) - strip(p[4])) + (strip(p[4]) - strip(r[4]))).values()) for p in P) for r in R]
print('non-holo texrect geometry diff: exact %d/%d median %s max %s' % (sum(d == 0 for d in ds), len(ds), st.median(ds), max(ds)))
# which non-holo rects differ: aggregate over best pairs, and are the moved rects a phase family (shared values)?
ro = collections.Counter(); po = collections.Counter()
for r in R:
    p = min(P, key=lambda p: sum(((strip(r[4]) - strip(p[4])) + (strip(p[4]) - strip(r[4]))).values()))
    ro.update(strip(r[4]) - strip(p[4])); po.update(strip(p[4]) - strip(r[4]))
print('non-holo only-retail', ro.most_common(6)); print('non-holo only-port', po.most_common(6))
ra = collections.Counter(); pa = collections.Counter()
for r in R: ra.update(set(strip(r[4])))
for p in P: pa.update(set(strip(p[4])))
print('rect positions: retail %d port %d shared %d' % (len(ra), len(pa), len(set(ra) & set(pa))))
always_r = {k for k, v in ra.items() if v == len(R)}; always_p = {k for k, v in pa.items() if v == len(P)}
print('present in every frame: retail %d port %d, same set: %s' % (len(always_r), len(always_p), always_r == always_p))
q = lambda t: [sorted(t)[int(len(t) * x)] for x in (0.1, 0.25, 0.5, 0.75, 0.9)]
print('tri quantiles retail', q([f[0] for f in R if f[0]]), 'port', q([f[0] for f in P]))
print('always port-not-retail', sorted(always_p - always_r)); print('always retail-not-port', sorted(always_r - always_p))
band = lambda g: sorted({k for k in g if 160 <= k[1] <= 230 and k[2] - k[0] > 40})
print('retail wide rects y160-230 (union, first 12):', sorted(set().union(*[band(r[4]) for r in R]))[:12])
print('port   wide rects y160-230 (union, first 12):', sorted(set().union(*[band(p[4]) for p in P]))[:12])
print('frames with any such rect: retail %d/%d port %d/%d' % (sum(bool(band(r[4])) for r in R), len(R), sum(bool(band(p[4])) for p in P), len(P)))
