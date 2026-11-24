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
s7870: every exact-span segment is also placed in phase terms (port phase ordinal from the port bin header, retail VI
width from the retail bin header), so pre-flight islands vs in-flight diffs are separated without a side script.
Controls (iron rule 1, same run): --plant moves one triangle's YH by one sub-scanline in a port frame in the middle
of the exact run; it must turn exactly that frame non-exact (rc 3 otherwise). A second pair (e.g. the unpinned p2
arm) given with --neg PORT2.bin must NOT reach the same exact run (its state forks at t0).
s7876: flight is cut at the first >=3-frame tri-less run in the port stream at or after the longest exact run's start
(the post-flight blank, s7875: retail and port both show exactly one after flight, 10 frames, and the mission ticks end
there). Interior diffs are reported as "flight" (before the cut) and "post-flight" (after it: end-of-mission screen,
outside the det tick window, animation-phase class); rc 1 only for flight diffs. --no-cut restores the s7868 whole-span
rule. Flight starts at the first frame of the last port phase inside the exact span (earlier non-exact frames are
reported as pre-flight: the unpinned pre-tick-0 window, s7875/s7876). The plant control must land inside flight and must be counted as a flight diff.
usage: s7868_det_frame_cmp.py RETAIL.bin[.zst] PORT.bin[.zst] [--neg PORT2.bin] [--plant] [--min-tri 1] [--no-cut] [--port-end N] [--port-start N]
exit 0 = no flight interior diff, 1 = flight interior diffs (H-render), 2 = no alignment, 3 = control FAIL.
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
NOCUT = '--no-cut' in a
MINTRI = int(a[a.index('--min-tri') + 1]) if '--min-tri' in a else 1
# s7877: --port-end N scores only port frames [0:N) of BOTH port bins (pinned and --neg): the det-exact prefix when the
# pinned arm forks mid-flight (0x31=3: respawn tick 2313 vs retail 2314 moves the pairing offset -529 -> -528). Unset = whole bin.
PEND = int(a[a.index('--port-end') + 1]) if '--port-end' in a else None
# s7888: --port-start N drops port frames [0:N) of BOTH port bins (indices in the report are then relative to N): scores the
# flight phase at its own pairing offset when a pre-flight cinematic shifts it by a frame (0x31=15: intro -98, flight -99,
# votes 2372 / 1887). Unset = whole bin, byte-identical. With --port-end both are absolute indices.
PSTART = int(a[a.index('--port-start') + 1]) if '--port-start' in a else 0

def load(p, retail):
    fr = m.frames(rs64_zopen.materialize(p, tmp), retail)
    if not retail and PEND is not None: fr = fr[:PEND]
    if not retail and PSTART: fr = fr[PSTART:]
    return [c for c, _ in fr], [x for _, x in fr]   # (frame counters, port phase ordinal / retail VI width)

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

def blank_cut(P, start, n=3):   # s7876: first index of a >=n-frame tri-less run at/after start (the post-flight blank)
    s = None
    for j in range(start, len(P)):
        if ntri(P[j]) == 0:
            if s is None: s = j
            if j - s + 1 >= n: return s
        else: s = None
    return None

def report(tag, R, P, r):
    if r is None: print(f'{tag}: NO ALIGNMENT (no unique shared frame)'); return None
    j0, j1 = r['first'], r['last']
    inner = [j for j in range(j0, j1 + 1) if not r['eq'].get(j, False)]
    cut = None if NOCUT else blank_cut(P, r['run'][1]); r['cut'] = cut
    fs = j0   # s7876: flight starts at the last port phase (mission ticks); earlier diffs = pre-flight (unpinned pre-tick-0 window)
    if not NOCUT and PM is not None:
        fs = next((j for j in range(j0, j1 + 1) if PM[j] == PM[-1]), j0)
    r['fstart'] = fs
    pre = [j for j in inner if j < fs]
    fl = [j for j in inner if j >= fs and (cut is None or j < cut)]; po = [j for j in inner if cut is not None and j >= cut]
    rcut = cut + r['off'] if cut is not None else None
    rb = blank_cut(R, r['run'][1] + r['off']) if cut is not None else None
    fx = sum(1 for j in range(fs, (cut if cut is not None else j1 + 1)) if r['eq'].get(j, False))
    print(f"{tag}: post-flight cut port {cut} (paired retail {rcut}; retail's own first blank there {rb}"
          f"{' = paired' if rb == rcut else ' MISMATCH' if cut is not None else ''}); flight port[{fs}:{cut if cut is not None else j1 + 1}] "
          f"exact {fx} non-exact {len(fl)}; pre-flight port[{j0}:{fs}] non-exact {len(pre)}; post-flight non-exact {len(po)}")
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
    if PM is not None and RM is not None:   # s7870: place every segment in phase terms (port phase ordinal / retail VI width)
        ph = collections.OrderedDict()
        for j in range(j0, j1 + 1):
            key = (PM[j], RM[j + r['off']]); d = ph.setdefault(key, [0, 0, j, j]); d[0 if r['eq'].get(j, False) else 1] += 1; d[3] = j
        print('  phases in exact span (port phase / retail width: exact, non-exact, port range):')
        for (pp, rw), (ne, nn, a0, a1) in ph.items(): print(f'    phase {pp} / width {rw}: exact {ne} non-exact {nn} port[{a0}:{a1 + 1}]')
        firstN = [(e, a, b) for e, a, b in segs if not e]
        for e, a, b in firstN[:6] + firstN[-6:]:
            print(f'    N{b - a + 1}@{a}: port phase {PM[a]}..{PM[b]} retail width {RM[a + r["off"]]}..{RM[b + r["off"]]} ({kind(a)})')
    for j in (fl + po)[:12]:
        c, q = P[j], R[j + r['off']]
        d1 = c - q; d2 = q - c
        print(f'  port {j} / retail {j + r["off"]}: tris p={ntri(c)} r={ntri(q)}; port-only {sum(d1.values())} '
              f'retail-only {sum(d2.values())}; e.g. port {list(d1)[:1]} retail {list(d2)[:1]}'[:400])
    return fl

R, RM = load(a[0], True); P, PM = load(a[1], False); PM0 = PM
print(f'retail frames {len(R)}, port frames {len(P)}' + (f' (port frames from {PSTART}; indices relative)' if PSTART else ''))
def rl(M): # run-length (value@start(len)) of a whole-stream meta list
    o = []
    for i, x in enumerate(M):
        if o and o[-1][0] == x: o[-1][2] += 1
        else: o.append([x, i, 1])
    return ' '.join(f'{x}@{i}({n})' for x, i, n in o)[:600]
print('port phases (ordinal@start(frames)):', rl(PM)); print('retail widths (width@start(frames)):', rl(RM))
ntx = lambda c: sum(v for k, v in c.items() if k[0] != 'tri')
for ph in dict.fromkeys(PM):   # HUD presence per port phase: flight frames carry HUD texrects, intro cinematics none (s7870)
    js = [j for j, x in enumerate(PM) if x == ph]
    print(f'  port phase {ph}: {len(js)} frames, {sum(1 for j in js if ntx(P[j]))} with texrects (HUD/text)')
r = align(R, P); inner = report('pair', R, P, r)
if r is None: sys.exit(2)
rc = 0 if not inner else 1
if '--plant' in a:
    def plant(j):
        c = collections.Counter(P[j])
        k = next((k for k in c if k[0] == 'tri' and len(k) > 3), None)
        if k is None: return False
        g = list(k); g[3] = ((g[3] & ~0x3FFF) | ((g[3] + 1) & 0x3FFF))   # YH = low 14 bits of the 2nd word (k = tri, prim, w0, w1, ...) + 1 quantum
        c[k] -= 1; c[tuple(g)] += 1; c += collections.Counter(); P2 = P[:j] + [c] + P[j + 1:]
        r2 = align(R, P2); return r2 is not None and r2['eq'].get(j) is False and all(r2['eq'].get(i) == r['eq'].get(i) for i in r['eq'] if i != j)
    # s7891: plant in the middle of the exact FLIGHT span (was: the longest exact run, which is pre-flight once a pre-flight island
    # closes, and then failed the s7876 in-flight bar without saying whether the diff was caught); the first flight frame with a
    # tri at or after the middle. A second, informational plant sits in the longest run when that run is pre-flight.
    fe = r['cut'] if r['cut'] is not None else len(P)
    j = next((i for i in range((r['fstart'] + fe) // 2, fe) if any(k[0] == 'tri' for k in P[i])), (r['run'][1] + r['run'][2]) // 2)
    inflight = j >= r['fstart'] and j < fe
    ok = plant(j) and inflight   # s7876: the plant must sit inside flight, where a diff sets rc 1
    print(f'control plant (port frame {j}, one tri YH+1, in flight {inflight}): {"PASS caught" if ok else "FAIL"}')
    jr = (r['run'][1] + r['run'][2]) // 2
    if jr < r['fstart']:
        jr = next((i for i in range(jr, r['run'][2]) if any(k[0] == 'tri' for k in P[i])), jr)
        print(f'control plant pre-flight (port frame {jr}, longest exact run, informational): {"caught" if plant(jr) else "MISSED"}')
    if not ok: rc = 3
if '--neg' in a:
    N, NM = load(a[a.index('--neg') + 1], False); PM = NM; rn = align(R, N); report('neg', R, N, rn)
    # s7870: scope the neg control to the LAST port phase (flight): a pre-flight cinematic is deterministic in both arms
    # (pins act from mission tick 0), so a whole-run longest-run bar fails a correct unpinned arm (0x31=5: 2286 vs 2911).
    last = PM0[-1]; ex = lambda rr, M: 0 if rr is None else sum(1 for j, e in rr['eq'].items() if e and M[j] == last)
    ep, en = ex(r, PM0), ex(rn, NM); nl = sum(1 for x in PM0 if x == last)
    ok = ep > 0 and en < ep // 2
    print(f'control neg (unpinned arm exact frames in final port phase {last}: pinned {ep}/{nl}, unpinned {en}): {"PASS" if ok else "FAIL"}')
    if not ok: rc = 3
sys.exit(rc)
