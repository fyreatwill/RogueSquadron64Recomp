#!/usr/bin/env python3
"""s6979 G1e thread census (reads ROGUESQ_G1E_THREADS binary, events.cpp g1et). Per late / normal send_dl window (from
g1e_late_leg.py --windows): Gfx-thread samples split into ran (CPU gained), runnable-not-run (TH_STATE_RUNNING, ~0 CPU: preempted),
waiting (blocked: H-block); our process's other threads' CPU (cores-equivalent) and the top consumers (H-intra); per-CPU busy from
host ticks over the 10 ms tick window around it, split into the two perf levels by ranking CPUs (H-extern = CPUs busy beyond our
threads). usage: g1e_thread_census.py thr.bin [windows.txt] [--summary]"""
import sys, struct, bisect, collections
a = [x for x in sys.argv[1:] if not x.startswith('--')]
raw = open(a[0], 'rb').read(); o = 0; names = {}; S = []; T = []; K = []; sym = {}; base = None; E = []; P8 = []
while o + 16 <= len(raw):
    ty = raw[o]; n = raw[o + 1] if ty == 3 else struct.unpack_from('<H', raw, o + 2)[0]; t = struct.unpack_from('<d', raw, o + 8)[0]
    if ty == 1:
        if o + 16 + 8 * n > len(raw): break
        recs = [struct.unpack_from('<HBBI', raw, o + 16 + 8 * i) for i in range(n)]; S.append((t, recs)); o += 16 + 8 * n
    elif ty == 2:
        if o + 80 > len(raw): break
        names[n] = raw[o + 16:o + 80].split(b'\0')[0].decode(errors='replace') or f'?{n}'; o += 80
    elif ty == 3:
        if o + 16 + 16 * n > len(raw): break
        T.append((t, [struct.unpack_from('<4I', raw, o + 16 + 16 * c) for c in range(n)])); o += 16 + 16 * n
    elif ty == 4:
        n = raw[o + 1]
        if o + 16 + 8 * n > len(raw): break
        K.append((t, struct.unpack_from(f'<{n}Q', raw, o + 16))); o += 16 + 8 * n
    elif ty == 7:
        if o + 24 > len(raw): break
        E.append((t, raw[o + 1], struct.unpack_from('<I', raw, o + 4)[0], struct.unpack_from('<Q', raw, o + 16)[0])); o += 24
    elif ty == 8:
        if o + 32 > len(raw): break
        P8.append((t,) + struct.unpack_from('<3i', raw, o + 16)); o += 32
    elif ty == 5: base = struct.unpack_from('<Q', raw, o + 8)[0]; o += 16
    elif ty == 6:
        if o + 96 > len(raw): break
        ad = struct.unpack_from('<Q', raw, o + 8)[0]; sym[ad] = (raw[o + 16:o + 96].split(b'\0')[0].decode(errors='replace'), struct.unpack_from('<I', raw, o + 4)[0]); o += 96
    else: sys.exit(f'bad record type {ty} at {o}')
St = [s[0] for s in S]; Tt = [x[0] for x in T]
dur = St[-1] - St[0]; dt = [St[i + 1] - St[i] for i in range(len(St) - 1)]; dt.sort()
print(f'samples {len(S)} over {dur:.1f} s ({len(S) / dur:.0f}/s), interval p50 {dt[len(dt)//2]*1e3:.3f} p99 {dt[int(.99*len(dt))]*1e3:.3f} ms; threads named {len(names)}; tick rows {len(T)}')
cpu = collections.Counter()
for t, recs in S:
    for idx, st, pri, d in recs: cpu[idx] += d
print('top threads by CPU (cores-equivalent over run):')
for idx, ns in cpu.most_common(14): print(f'  {idx:3d} {names.get(idx, "?"):28s} {ns / 1e9 / dur:6.3f}')
gfx = [i for i, nm in names.items() if nm == 'Gfx Thread']
if not gfx: sys.exit('no Gfx Thread')
G = gfx[0]
# per-CPU busy fraction over whole run -> rank CPUs; top-5 by our-load correlation is ambiguous, so report raw per-CPU means
ncpu = len(T[0][1])
def busy(i0, i1):
    out = []
    for c in range(ncpu):
        u0 = T[i0][1][c]; u1 = T[i1][1][c]; d = [u1[k] - u0[k] for k in range(4)]; tot = sum(d)
        out.append((d[0] + d[1] + d[3]) / tot if tot else float('nan'))
    return out
whole = busy(0, len(T) - 1)
print('per-CPU busy over run: ' + ' '.join(f'{c}:{b:.2f}' for c, b in enumerate(whole)))
if len(a) < 2: sys.exit(0)
def window(t0, t1):
    i0 = bisect.bisect_left(St, t0); i1 = bisect.bisect_right(St, t1)
    ran = rn = wt = 0; oth = collections.Counter(); gcpu = 0; strip = ''; offc = collections.Counter(); pri = collections.Counter()
    for t, recs in S[i0:i1]:
        seen = False; c = 'w'
        for idx, st, pri_, d in recs:
            if idx == G:
                seen = True; gcpu += d
                if d > 200_000: ran += 1; c = 'R'
                elif st == 1: rn += 1; c = 'r'
                else: wt += 1
                pri[pri_] += 1
            else: oth[idx] += d
        if not seen: wt += 1  # not in record = waiting with no state change
        strip += c
        if c != 'R':
            for idx, st, pri_, d in recs:
                if idx != G: offc[idx] += d
    n = max(1, i1 - i0); w = max(1e-6, t1 - t0)
    j0 = max(0, bisect.bisect_right(Tt, t0) - 1); j1 = min(len(T) - 1, bisect.bisect_left(Tt, t1))
    if j1 <= j0: j1 = min(len(T) - 1, j0 + 1)
    b = busy(j0, j1)
    return dict(n=n, ran=ran / n, rn=rn / n, wt=wt / n, gcpu=gcpu / 1e6, oth=sum(oth.values()) / 1e9 / w, top=oth.most_common(3), b=b, tw=(Tt[j1] - Tt[j0]) * 1e3, strip=strip, offc=offc.most_common(4), pri=dict(pri))
W = collections.defaultdict(list)
for l in open(a[1]):
    p = l.split(); te = float(p[1]); sd = float(p[2]); W[p[0]].append((te, sd, float(p[3]), window(te - sd / 1e3, te)))
pc = lambda v, q: sorted(v)[int(q * (len(v) - 1))] if v else float('nan')
for k in ('norm', 'late'):
    R = W[k]
    if not R: continue
    print(f'{k}: n={len(R)}  gfx ran/runnable-not-run/waiting frac p50 ' + '/'.join(f'{pc([r[3][f] for r in R], .5):.2f}' for f in ('ran', 'rn', 'wt')) +
          f'  other-threads cores p50 {pc([r[3]["oth"] for r in R], .5):.2f} p90 {pc([r[3]["oth"] for r in R], .9):.2f}' +
          f'  CPUs>80% busy p50 {pc([sum(x > .8 for x in r[3]["b"]) for r in R], .5)}')
print('per late window: t_end | sd | sdc | samples | gfx ran/rn/wait | other cores | top others (ms) | CPUs busy>80%% of %d (tick win ms) | busy per CPU' % ncpu)
for te, sd, sdc, r in W['late']:
    top = ', '.join(f'{names.get(i, "?")}:{d / 1e6:.1f}' for i, d in r['top'])
    print(f'  {te:.3f} | {sd:5.2f} | {sdc:5.2f} | {r["n"]:3d} | {r["ran"]:.2f}/{r["rn"]:.2f}/{r["wt"]:.2f} | {r["oth"]:.2f} | {top} | {sum(x > .8 for x in r["b"])} ({r["tw"]:.0f}) | ' + ''.join('%d' % min(9, int(x * 10)) for x in r['b']))
    print(f'     strip {r["strip"]}  gfx curpri {r["pri"]}')
    print('     while gfx not running: ' + ', '.join(f'{names.get(i, "?")}:{d / 1e6:.2f}' for i, d in r['offc']))
import random
random.seed(1); print('normal examples:')
for te, sd, sdc, r in random.sample(W['norm'], min(4, len(W['norm']))):
    print(f'  {te:.3f} | {sd:5.2f} | {sdc:5.2f} | strip {r["strip"]} | pri {r["pri"]}')

# s6979b: Gfx-thread stacks while WAITING inside send_dl windows (late vs normal)
if K:
    import subprocess, os
    Kt = [k[0] for k in K]
    def stacks(R):
        out = []
        for te, sd, sdc, r in R:
            i0 = bisect.bisect_left(Kt, te - sd / 1e3); i1 = bisect.bisect_right(Kt, te); out += [K[i][1] for i in range(i0, i1)]
        return out
    SL, SN = stacks(W['late']), stacks(W['norm'])
    exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build', 'RogueSquadron64Recomp')
    allad = sorted({x for st in SL + SN for x in st})
    nm = {ad: (sym.get(ad, ('?', 0))[0] + '+%d' % sym.get(ad, ('?', 0))[1]) for ad in allad}
    if base:
        mine = [ad for ad in allad if base <= ad < base + 0x10000000]
        for c in range(0, len(mine), 400):
            ch = mine[c:c + 400]
            res = subprocess.run(['atos', '-o', exe, '-l', hex(base)] + [hex(x) for x in ch], capture_output=True, text=True).stdout.split('\n')
            for ad, l in zip(ch, res):
                if l.strip(): nm[ad] = l.strip().split(' (in ')[0][:70]
    print(f'Gfx WAITING stacks: inside late windows {len(SL)}, inside normal windows {len(SN)} (stack records total {len(K)}, image base {hex(base or 0)})')
    for lab, SS in (('late', SL), ('normal', SN)):
        c = collections.Counter(' <- '.join(nm[x] for x in st[:7]) for st in SS)
        print(f'  {lab}: top signatures')
        for sig, n in c.most_common(6): print(f'    {n:4d}  {sig}')
