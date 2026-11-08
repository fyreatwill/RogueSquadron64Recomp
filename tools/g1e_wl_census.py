#!/usr/bin/env python3
"""s6988 G1e: run vs runnable-not-running time of the RT64 workload thread and the Gfx thread on late vs normal presents
(H-preempt vs H-work vs H-shared for the residual lates left once ROGUESQ_WL_QOS=1 is on, s6987).
Inputs: ROGUESQ_G1E_THREADS binary (events.cpp g1et, mach s clock) + the windows file of
`g1e_vi_phase.py ... --windows OUT` ('late|norm R_end sd W rend pick ksd rw t', corrected chain).
Windows per present: WL render [W-rend, W] (workload thread), WL pick [R, R+pick] (wake gap, only pick>0.5 ms),
Gfx send_dl [R-sd, R] (Gfx thread). Per window and thread: cpu ms (sum of sampled cpu deltas), runnable-not-running ms
(TH_STATE_RUNNING samples that gained <=200 us, x sample interval), waiting ms; plus the other thread's cpu inside the WL
render window (H-shared) and CPUs >80% busy from host ticks (10 ms rows).
Positive control (s6987): at WL_QOS=0 the late pick window (1.3-1.6 ms wake gap) must read runnable-not-running.
usage: g1e_wl_census.py thr.bin windows.txt [--list N]"""
import sys, struct, bisect, collections
a = [x for x in sys.argv[1:] if not x.startswith('--')]
nlist = int(sys.argv[sys.argv.index('--list') + 1]) if '--list' in sys.argv else 0
if nlist: a = [x for x in a if x != str(nlist)]
raw = open(a[0], 'rb').read(); o = 0; names = {}; S = []; T = []
while o + 16 <= len(raw):
    ty = raw[o]; n = raw[o + 1] if ty in (3, 4) else struct.unpack_from('<H', raw, o + 2)[0]; t = struct.unpack_from('<d', raw, o + 8)[0]
    if ty == 1:
        if o + 16 + 8 * n > len(raw): break
        S.append((t, [struct.unpack_from('<HBBI', raw, o + 16 + 8 * i) for i in range(n)])); o += 16 + 8 * n
    elif ty == 2:
        if o + 80 > len(raw): break
        names[n] = raw[o + 16:o + 80].split(b'\0')[0].decode(errors='replace'); o += 80
    elif ty == 3:
        if o + 16 + 16 * n > len(raw): break
        T.append((t, [struct.unpack_from('<4I', raw, o + 16 + 16 * c) for c in range(n)])); o += 16 + 16 * n
    elif ty == 4: o += 16 + 8 * raw[o + 1]
    elif ty == 7: o += 24
    elif ty == 8: o += 32
    elif ty == 5: o += 16
    elif ty == 6: o += 96
    else: sys.exit(f'bad record type {ty} at {o}')
St = [s[0] for s in S]; Tt = [x[0] for x in T]
ids = lambda nm: [i for i, x in names.items() if x == nm]
GF, WL = ids('Gfx Thread'), ids('RT64 Workload')
if not GF or not WL: sys.exit(f'threads missing: gfx {GF} wl {WL}')
GF, WL = set(GF), set(WL)
ncpu = len(T[0][1])
def busy(t0, t1):
    j0 = max(0, bisect.bisect_right(Tt, t0) - 1); j1 = min(len(T) - 1, max(j0 + 1, bisect.bisect_left(Tt, t1)))
    n = 0
    for c in range(ncpu):
        d = [T[j1][1][c][k] - T[j0][1][c][k] for k in range(4)]; tot = sum(d)
        n += bool(tot) and (d[0] + d[1] + d[3]) / tot > .8
    return n
def win(t0, t1, who, other):
    # samples whose interval (prev sample, this sample] overlaps [t0, t1]
    i0 = bisect.bisect_right(St, t0); i1 = bisect.bisect_left(St, t1) + 1
    cpu = rn = wt = ocpu = 0.0; strip = ''; pri = collections.Counter()
    for i in range(max(1, i0), min(len(S), i1)):
        dt = St[i] - St[i - 1]; ov = max(0.0, min(St[i], t1) - max(St[i - 1], t0)); f = ov / dt if dt > 0 else 0
        c = 'w'; seen = False
        for idx, st, p, d in S[i][1]:
            if idx in who:
                seen = True; cpu += d * f / 1e6; pri[p] += 1
                if d > 200_000: c = 'R'
                elif st == 1: c = 'r'; rn += ov * 1e3
                else: wt += ov * 1e3
            elif idx in other: ocpu += d * f / 1e6
        if not seen: wt += ov * 1e3
        strip += c
    return dict(wall=(t1 - t0) * 1e3, cpu=cpu, rn=rn, wt=wt, ocpu=ocpu, strip=strip, pri=pri)
rows = collections.defaultdict(list)
for l in open(a[1]):
    p = l.split(); k = p[0]; R, sd, Wt, rend, pick, ksd, rw, tt = map(float, p[1:9])
    if R - sd / 1e3 < St[0] or Wt > St[-1]: continue
    r = dict(R=R, t=tt, sd=sd, rend=rend, pick=pick, ksd=ksd, rw=rw)
    r['wr'] = win(Wt - rend / 1e3, Wt, WL, GF)          # workload render window, other = Gfx
    r['gs'] = win(R - sd / 1e3, R, GF, WL)              # Gfx send_dl window, other = workload
    r['wp'] = win(R, R + pick / 1e3, WL, GF) if pick > 0.5 else None
    r['bz'] = busy(Wt - rend / 1e3, Wt)
    rows[k].append(r)
pc = lambda v, q: sorted(v)[int(q * (len(v) - 1))] if v else float('nan')
def auc(x, y): return sum((u > v) + 0.5 * (u == v) for u in x for v in y) / (len(x) * len(y)) if x and y else float('nan')
L, N = rows['late'], rows['norm']; Ns = N[::max(1, len(N) // 3000)]
print(f'samples {len(S)} ({len(S) / (St[-1] - St[0]):.0f}/s), late {len(L)} normal {len(N)}; WL ids {sorted(WL)} Gfx ids {sorted(GF)}')
F = [('WL render wall', lambda r: r['wr']['wall']), ('WL render cpu', lambda r: r['wr']['cpu']),
     ('WL render rn', lambda r: r['wr']['rn']), ('WL render wait', lambda r: r['wr']['wt']),
     ('WL cpu/wall', lambda r: r['wr']['cpu'] / max(.01, r['wr']['wall'])), ('Gfx cpu in WL render', lambda r: r['wr']['ocpu']),
     ('Gfx sd wall', lambda r: r['gs']['wall']), ('Gfx sd cpu', lambda r: r['gs']['cpu']), ('Gfx sd rn', lambda r: r['gs']['rn']),
     ('Gfx sd wait', lambda r: r['gs']['wt']), ('Gfx cpu/wall', lambda r: r['gs']['cpu'] / max(.01, r['gs']['wall'])),
     ('WL cpu in Gfx sd', lambda r: r['gs']['ocpu']), ('CPUs>80% (WL rend)', lambda r: r['bz'])]
print('  field                 late p10/p50/p90        | normal p10/p50/p90       AUC')
for nm, fn in F:
    x = [fn(r) for r in L]; y = [fn(r) for r in N]
    print(f'  {nm:20s} ' + ' '.join(f'{pc(x, q):7.2f}' for q in (.1, .5, .9)) + '  | ' + ' '.join(f'{pc(y, q):7.2f}' for q in (.1, .5, .9)) + f'  {auc(x, [fn(r) for r in Ns]):.2f}')
for k, R_ in (('late', L), ('norm', N)):
    P_ = [r['wp'] for r in R_ if r['wp']]
    if P_: print(f'  pick>0.5 ms {k}: n={len(P_)} wall p50 {pc([w["wall"] for w in P_], .5):.2f} rn p50 {pc([w["rn"] for w in P_], .5):.2f}'
                 f' cpu p50 {pc([w["cpu"] for w in P_], .5):.2f} wait p50 {pc([w["wt"] for w in P_], .5):.2f} (rn+wait frac rn {sum(w["rn"] for w in P_) / max(1e-9, sum(w["rn"] + w["wt"] for w in P_)):.2f})')
    else: print(f'  pick>0.5 ms {k}: n=0')
# late class split: excess render time explained by runnable-not-running (preempt) vs cpu (work) vs waiting (block)
nr = pc([r['wr']['wall'] for r in N], .5); nc = pc([r['wr']['cpu'] for r in N], .5)
cls = collections.Counter()
for r in L:
    ex = r['wr']['wall'] - nr; dc = r['wr']['cpu'] - nc; w = r['wr']
    cls['preempt' if w['rn'] >= max(dc, w['wt']) and w['rn'] > 1 else 'work' if dc >= max(w['rn'], w['wt']) and dc > 1 else 'block' if w['wt'] > 1 else 'small'] += 1
print(f'  late WL-render class (excess vs normal p50 wall {nr:.2f} cpu {nc:.2f}): ' + ' '.join(f'{k}={v}' for k, v in cls.most_common()))
cls = collections.Counter()
ng = pc([r['gs']['cpu'] for r in N], .5)
for r in L:
    g = r['gs']; dc = g['cpu'] - ng
    cls['preempt' if g['rn'] >= max(dc, g['wt']) and g['rn'] > 1 else 'work' if dc >= max(g['rn'], g['wt']) and dc > 1 else 'block' if g['wt'] > 1 else 'small'] += 1
print(f'  late Gfx-sd class (normal p50 cpu {ng:.2f}): ' + ' '.join(f'{k}={v}' for k, v in cls.most_common()))
for r in sorted(L, key=lambda r: -r['rw'])[:nlist]:
    w, g = r['wr'], r['gs']
    print(f"   t={r['t']:7.2f} rw {r['rw']:5.2f} rend {r['rend']:5.2f} cpu {w['cpu']:5.2f} rn {w['rn']:4.1f} wt {w['wt']:4.1f} strip {w['strip']:12s} pri {dict(w['pri'])}"
          f" | sd {r['sd']:5.2f} cpu {g['cpu']:5.2f} rn {g['rn']:4.1f} wt {g['wt']:4.1f} | busy {r['bz']}")
# s6988b: the RT64 upload threads the Gfx thread waits on in late send_dl windows (TextureCache::waitForGPUUploads ->
# "RT64 Texture", FramebufferRenderer::waitForUploaders -> "RT64 Buffer" x N): their cpu and runnable-not-running ms there.
for tn in ('RT64 Texture', 'RT64 Buffer', 'RT64 Workload'):
    th = set(ids(tn))
    if not th: continue
    out = {'late': L, 'norm': N[::max(1, len(N) // 3000)]}
    def g(r):
        w = win(r['R'] - r['sd'] / 1e3, r['R'], th, set()); return w
    xs = {k: [g(r) for r in v] for k, v in out.items()}
    print(f'  {tn} (x{len(th)}) in Gfx sd windows: ' + ' | '.join(f"{k} cpu p50/p90 {pc([w['cpu'] for w in v], .5):.2f}/{pc([w['cpu'] for w in v], .9):.2f}"
          f" rn p50/p90 {pc([w['rn'] for w in v], .5):.2f}/{pc([w['rn'] for w in v], .9):.2f} rn>0.5ms {sum(w['rn'] > .5 for w in v) / max(1, len(v)):.2f}" for k, v in xs.items()))
