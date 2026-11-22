#!/usr/bin/env python3
"""s7821 G3: split a retail (rdplog RS64_RDP_BIN) and a port (RS64_RDP_BIN_PORT) RDP stream into SCREENS and match per screen.

Frame = commands between FULL_SYNCs (same parser as g3_rdp_frame_match.py). Screen identity = the set of texrect
GEOMETRIES (xh,yh,xl,yl; PRIM and tris ignored). A new segment starts when a frame's geometry set has Jaccard < --jac
(default 0.5) against the running segment's first stable frame. Segments shorter than --min frames are merged away
(fades). For each retail segment the best port segment (texrect-geometry Jaccard of their union sets) is paired and
scored on the last --k frames of each with the g3_rdp_frame_match signature (texrects with PRIM + tri PRIM multiset)
and two decompositions: texrect geometry only, and geometry without PRIM (texrects + tri count).
Control: each retail segment against the WORST-overlapping port segment (must not match; median > paired median).
--elements RW:PW (e.g. 512:5 = retail VI width 512, port phase ordinal 5): element-level test for animated screens
(hangar) whose arms render at different rates, so whole frames never pair: the fraction of retail texrect instances
whose geometry occurs ANYWHERE in the port screen, all and excluding breathing glyph strips (w 54-61, h 16.5-21.5),
with controls: same test against port phase --ctl-phase (must be ~0) and a +0.25 px planted shift (must drop to ~0).
usage: s7821_rdp_screen_segments.py RETAIL.bin PORT.bin [--k 120] [--jac 0.5] [--min 20] [--elements 512:5 --ctl-phase 4]
"""
import struct, sys, collections
sys.path.insert(0, __file__.rsplit('/', 1)[0])
try:
    from rs64_zopen import zbytes as _zb
    def readall(p): return bytes(_zb(p))
except Exception:
    def readall(p): return open(p, 'rb').read()

def frames(path, retail):
    f = readall(path); H = 20 if retail else 16; o = 0; out = []; cur = []; prim = None; meta = None
    buf = bytearray(); bmeta = []
    while o + H <= len(f):
        w = struct.unpack_from('<5I' if retail else '<4I', f, o)
        ln = w[3] if retail else w[2]; m = w[2] if retail else w[3]   # retail: vi_width; port: phase ordinal
        buf += f[o + H:o + H + ln]; bmeta.append((len(buf), m)); o += H + ln
    cat = bytes(buf); a = 0; mi = 0
    g = lambda i: struct.unpack_from('<I', cat, i)[0]
    while a + 8 <= len(cat):
        while mi < len(bmeta) - 1 and bmeta[mi][0] <= a: mi += 1
        w0, w1 = g(a), g(a + 4); op = (w0 >> 24) & 0x3F; n = 8
        if 0x08 <= op <= 0x0F:
            n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0); cur.append(('tri', prim))
        elif op in (0x24, 0x25):
            n = 16; cur.append((((w1 >> 12) & 0xFFF) / 4, (w1 & 0xFFF) / 4, ((w0 >> 12) & 0xFFF) / 4, (w0 & 0xFFF) / 4, prim))
        elif op == 0x3A: prim = '%08X' % w1
        elif op == 0x29:
            if cur: out.append((collections.Counter(cur), bmeta[mi][1]))
            cur = []
        a += n
    return out

def geom(c): return frozenset(k[:4] for k in c if k[0] != 'tri')
def jac(a, b): return len(a & b) / len(a | b) if (a | b) else 1.0

def segments(fr, J, MIN):
    segs = []; s0 = 0; ref = geom(fr[0][0]) if fr else frozenset()
    for i in range(1, len(fr)):
        gi = geom(fr[i][0])
        if jac(gi, ref) < J or fr[i][1] != fr[i - 1][1]:   # geometry jump or width/phase change
            segs.append((s0, i)); s0 = i; ref = gi
    segs.append((s0, len(fr)))
    segs = [s for s in segs if s[1] - s[0] >= MIN]
    return segs

def sig_full(c): return c
def sig_geom(c): return collections.Counter({k[:4]: v for k, v in c.items() if k[0] != 'tri'})
def sig_noprim(c):
    d = collections.Counter()
    for k, v in c.items(): d[('tri',) if k[0] == 'tri' else k[:4]] += v
    return d
def score(R, P, f):
    Rs = [f(c) for c in R]; Ps = [f(c) for c in P]
    ds = [min(sum(((c - q) + (q - c)).values()) for q in Ps) for c in Rs]
    return sum(d == 0 for d in ds), len(ds), sorted(ds)[len(ds) // 2], max(ds)

if __name__ == '__main__':
    a = sys.argv; opt = lambda n, d: type(d)(a[a.index(n) + 1]) if n in a else d
    K, J, MIN = opt('--k', 120), opt('--jac', 0.5), opt('--min', 20)
    R = frames(a[1], True); P = frames(a[2], False)
    print(f'frames retail={len(R)} port={len(P)}')
    if '--elements' in a:
        rw, pw = map(int, opt('--elements', '512:5').split(':')); cp = opt('--ctl-phase', 4)
        Rh = [c for c, m in R if m == rw]; Ph = [c for c, m in P if m == pw]; Pc = [c for c, m in P if m == cp]
        breath = lambda k: 54 <= k[2] - k[0] <= 61 and 16.5 <= k[3] - k[1] <= 21.5
        U = lambda F: set(k[:4] for c in F for k in c if k[0] != 'tri')
        def fr_(F, Us, excl):
            n = h = 0
            for c in F:
                for k, v in c.items():
                    if k[0] == 'tri' or (excl and breath(k)): continue
                    n += v; h += v * (k[:4] in Us)
            return round(h / max(n, 1), 4), n
        UP, UC = U(Ph), U(Pc)
        Rs = [collections.Counter({((k[0] + 0.25,) + k[1:]) if k[0] != 'tri' else k: v for k, v in c.items()}) for c in Rh]
        print(f'elements: retail frames {len(Rh)} port frames {len(Ph)} ctl frames {len(Pc)}')
        for excl in (False, True):
            print(f"  {'non-breathing' if excl else 'all'}: R-in-P {fr_(Rh, UP, excl)} P-in-R {fr_(Ph, U(Rh), excl)} "
                  f"ctl R-in-ctlphase {fr_(Rh, UC, excl)} plant+0.25 {fr_(Rs, UP, excl)}")
        sys.exit(0)
    if '--windows' in a:   # s7822: explicit frame windows for animated sub-screens the jaccard segmenter fragments
        # --windows r0:r1,p0:p1,c0:c1  (retail window, port window, port control window); scores the last K of each
        (r0, r1), (p0, p1), (c0, c1) = [tuple(map(int, w.split(':'))) for w in opt('--windows', '').split(',')]
        Rk = [c for c, _ in R[max(r0, r1 - K):r1]]; Pk = [c for c, _ in P[p0:p1]]; Ck = [c for c, _ in P[c0:c1]]
        plant = [collections.Counter({((k[0] + 0.25,) + k[1:]) if k[0] != 'tri' else k: v for k, v in c.items()}) for c in Rk]
        for nm, f in (('full', sig_full), ('geom', sig_geom), ('noprim', sig_noprim)):
            print(f'  {nm}: R[{max(r0, r1 - K)}:{r1}] vs P[{p0}:{p1}] {score(Rk, Pk, f)} || ctl P[{c0}:{c1}] {score(Rk, Ck, f)} '
                  f'|| plant+0.25 {score(plant, Pk, f)}')
        UR = set(k[:4] for c in Rk for k in c if k[0] != 'tri'); UP = set(k[:4] for c in Pk for k in c if k[0] != 'tri')
        print(f'  geom only-retail {sorted(UR - UP)[:12]} n={len(UR - UP)} | only-port {sorted(UP - UR)[:12]} n={len(UP - UR)}')
        # element test over the windows; scale-animated strips (54-66 x 16.5-22 px) excluded in the second row
        br = lambda k: 54 <= k[2] - k[0] <= 66 and 16.5 <= k[3] - k[1] <= 22
        UC = set(k[:4] for c in Ck for k in c if k[0] != 'tri')
        def ef(F, Us, excl):
            n = h = 0
            for c in F:
                for k, v in c.items():
                    if k[0] == 'tri' or (excl and br(k)): continue
                    n += v; h += v * (k[:4] in Us)
            return round(h / max(n, 1), 4), n
        for excl in (False, True):
            print(f"  elements {'non-strip' if excl else 'all'}: R-in-P {ef(Rk, UP, excl)} P-in-R {ef(Pk, UR, excl)} "
                  f"ctl R-in-C {ef(Rk, UC, excl)} plant R+0.25-in-P {ef(plant, UP, excl)}")
        if excl:
            miss = collections.Counter(k[:4] for c in Rk for k in c if k[0] != 'tri' and not br(k) and k[:4] not in UP)
            print('  non-strip retail misses (w,h):', collections.Counter((round(k[2]-k[0],2), round(k[3]-k[1],2)) for k in miss).most_common(8))
        sys.exit(0)
    RS = segments(R, J, MIN); PS = segments(P, J, MIN)
    def desc(fr, s, lab):
        u = frozenset().union(*(geom(fr[i][0]) for i in range(*s))); mids = fr[(s[0] + s[1]) // 2]
        ntri = sum(v for k, v in mids[0].items() if k[0] == 'tri'); ntr = sum(v for k, v in mids[0].items() if k[0] != 'tri')
        return u, f'{lab} frames {s[0]}-{s[1]} (n={s[1]-s[0]}) meta {fr[s[0]][1]}..{fr[s[1]-1][1]} mid: texrects {ntr} tris {ntri} geomset {len(u)}'
    Ru = []; Pu = []
    for i, s in enumerate(RS): u, t = desc(R, s, f'R{i}'); Ru.append(u); print(t)
    for i, s in enumerate(PS): u, t = desc(P, s, f'P{i}'); Pu.append(u); print(t)
    print('pairs (retail seg -> best port seg by geomset jaccard; ctl = worst port seg):')
    for i, s in enumerate(RS):
        js = [jac(Ru[i], u) for u in Pu]; b = max(range(len(js)), key=js.__getitem__); w = min(range(len(js)), key=js.__getitem__)
        Rk = [R[j][0] for j in range(max(s[0], s[1] - K), s[1])]
        pb = PS[b]; Pk = [P[j][0] for j in range(max(pb[0], pb[1] - K), pb[1])]
        pw = PS[w]; Pw = [P[j][0] for j in range(max(pw[0], pw[1] - K), pw[1])]
        print(f'  R{i} -> P{b} jac {js[b]:.2f} | full {score(Rk, Pk, sig_full)} geom {score(Rk, Pk, sig_geom)} '
              f'noprim {score(Rk, Pk, sig_noprim)} || ctl P{w} jac {js[w]:.2f} full {score(Rk, Pw, sig_full)} geom {score(Rk, Pw, sig_geom)}')
