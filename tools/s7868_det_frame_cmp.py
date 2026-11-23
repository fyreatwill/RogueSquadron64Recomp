#!/usr/bin/env python3
"""s7868 G3: per-frame EXACT render oracle on a det-pinned pair (port game state = retail tick for tick).

The det sweep (s7832-s7867) showed the pinned port reproduces retail's guest state bit-for-bit for whole missions (or up
to an audio-clock fork). On those ticks the display list is built from identical state, so every RDP frame must be
identical too: any frame that differs is a port render defect (RSP ucode emulation, DL patch, our fixups), not timing.

Frame = commands between FULL_SYNCs (tools/s7821_rdp_screen_segments.frames with --tri-geom): a multiset of every
triangle keyed by its exact RDP edge coefficients + PRIM colour, and every texrect by geometry + PRIM (HUD, reticle).
Alignment: each frame whose signature is unique on BOTH sides votes an offset (retail index - port index); the
winning offset defines the pairing, and the longest exactly-matching run under it is reported, with every
non-exact frame inside [first exact, last exact] listed (those are the H-render candidates: diffs where both
neighbours match).
Controls (iron rule 1, same run): --plant moves one triangle's YH by one sub-scanline in a port frame in the middle
of the exact run; it must turn exactly that frame non-exact (rc 3 otherwise). A second pair (e.g. the unpinned p2
arm) given with --neg PORT2.bin must NOT reach the same exact run (its state forks at t0).
usage: s7868_det_frame_cmp.py RETAIL.bin[.zst] PORT.bin[.zst] [--neg PORT2.bin] [--plant] [--min-tri 1]
exit 0 = no interior diff, 1 = interior diffs (H-render), 2 = no alignment, 3 = control FAIL.
"""
import sys, os, collections, importlib.util, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rs64_zopen
a = sys.argv[1:]
if len(a) < 2 or a[0].startswith('-'): print(__doc__); sys.exit(2)
sys.argv.append('--tri-geom')
sp = importlib.util.spec_from_file_location('seg', os.path.join(HERE, 's7821_rdp_screen_segments.py'))
m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
tmp = tempfile.mkdtemp(prefix='s7868_')
MINTRI = int(a[a.index('--min-tri') + 1]) if '--min-tri' in a else 1

def load(p, retail):
    fr = m.frames(rs64_zopen.materialize(p, tmp), retail)
    return [c for c, _ in fr]

def sig(c): return hash(frozenset(c.items()))
def ntri(c): return sum(v for k, v in c.items() if k[0] == 'tri')

def align(R, P):
    rs = [sig(c) for c in R]; ps = [sig(c) for c in P]
    rc = collections.Counter(rs); pc = collections.Counter(ps); rpos = {h: i for i, h in enumerate(rs)}
    votes = collections.Counter(rpos[h] - j for j, h in enumerate(ps)
                                if rc[h] == 1 and pc[h] == 1 and h in rpos and ntri(P[j]) >= MINTRI)
    if not votes: return None
    off = votes.most_common(1)[0][0]
    eq = [(j, rs[j + off] == ps[j]) for j in range(len(P)) if 0 <= j + off < len(R)]
    best = (0, 0, 0); s = None   # longest exact run (len, start, end) in port indices
    for j, e in eq:
        if e and s is None: s = j
        if not e and s is not None:
            if j - s > best[0]: best = (j - s, s, j)
            s = None
    if s is not None and eq[-1][0] + 1 - s > best[0]: best = (eq[-1][0] + 1 - s, s, eq[-1][0] + 1)
    ex = [j for j, e in eq if e]
    return dict(off=off, votes=votes.most_common(4), eq=dict(eq), run=best, first=ex[0] if ex else None,
                last=ex[-1] if ex else None, nexact=len(ex), npair=len(eq))

def report(tag, R, P, r):
    if r is None: print(f'{tag}: NO ALIGNMENT (no unique shared frame)'); return None
    j0, j1 = r['first'], r['last']
    inner = [j for j in range(j0, j1 + 1) if not r['eq'].get(j, False)]
    print(f"{tag}: offset retail-port {r['off']} votes {r['votes']}; paired {r['npair']} frames, exact {r['nexact']}; "
          f"longest exact run port[{r['run'][1]}:{r['run'][2]}] ({r['run'][0]} frames); exact span port[{j0}:{j1 + 1}]; "
          f"interior non-exact {len(inner)}")
    segs = []   # run-length map of the exact span: E = exact, N = non-exact (with the kind of the first diff)
    for j in range(j0, j1 + 1):
        e = r['eq'].get(j, False)
        if segs and segs[-1][0] == e: segs[-1][2] = j
        else: segs.append([e, j, j])
    def kind(j):
        c, q = P[j], R[j + r['off']]
        if ntri(c) != ntri(q): return 'tri-count'
        dt = sum(((c - q) + (q - c)).values()); dx = sum(1 for k in (c - q) if k[0] != 'tri') + sum(1 for k in (q - c) if k[0] != 'tri')
        return 'texrect/HUD' if dx and dx == dt else ('tri-geom' if not dx else 'tri+texrect')
    print('  map: ' + ' '.join(f"{'E' if e else 'N'}{b - a + 1}" + ('' if e else f'@{a}({kind(a)})') for e, a, b in segs)[:1500])
    for j in inner[:12]:
        c, q = P[j], R[j + r['off']]
        d1 = c - q; d2 = q - c
        print(f'  port {j} / retail {j + r["off"]}: tris p={ntri(c)} r={ntri(q)}; port-only {sum(d1.values())} '
              f'retail-only {sum(d2.values())}; e.g. port {list(d1)[:1]} retail {list(d2)[:1]}'[:400])
    return inner

R = load(a[0], True); P = load(a[1], False)
print(f'retail frames {len(R)}, port frames {len(P)}')
r = align(R, P); inner = report('pair', R, P, r)
if r is None: sys.exit(2)
rc = 0 if not inner else 1
if '--plant' in a:
    j = (r['run'][1] + r['run'][2]) // 2; c = collections.Counter(P[j])
    k = next(k for k in c if k[0] == 'tri' and len(k) > 3)
    g = list(k); g[3] = ((g[3] & ~0x3FFF) | ((g[3] + 1) & 0x3FFF))   # YH = low 14 bits of the 2nd word (k = tri, prim, w0, w1, ...) + 1 quantum
    c[k] -= 1; c[tuple(g)] += 1; c += collections.Counter(); P2 = P[:j] + [c] + P[j + 1:]
    r2 = align(R, P2); ok = r2 is not None and r2['eq'].get(j) is False and all(r2['eq'].get(i) == r['eq'].get(i) for i in r['eq'] if i != j)
    print(f'control plant (port frame {j}, one tri YH+1): {"PASS caught" if ok else "FAIL"}')
    if not ok: rc = 3
if '--neg' in a:
    N = load(a[a.index('--neg') + 1], False); rn = align(R, N); report('neg', R, N, rn)
    ok = rn is None or rn['run'][0] < r['run'][0] // 2
    print(f'control neg (unpinned arm must not match as long): {"PASS" if ok else "FAIL"}')
    if not ok: rc = 3
sys.exit(rc)
