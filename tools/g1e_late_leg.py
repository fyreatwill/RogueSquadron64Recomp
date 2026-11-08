#!/usr/bin/env python3
"""s6975 G1e late-leg split (fork of g1e_tl_present.py): per single-vsync-late present, its kick chain plus the gfx thread's
send_dl wall vs thread-CPU ms (R rows of ROGUESQ_G1E_GRING). Per late present: H-sched (kick phase after VI late), H-rsp-host
(rsp leg long, wall-cpu gap large = gfx thread preempted), H-rsp-work (rsp long and cpu long = more ucode work).
Original doc: s6967 G1e: per-present join of the s6711 timeline (ROGUESQ_G1E_TL, steady-clock us) to the present ring (mach s), through the
G rows of ROGUESQ_G1E_GRING (each carries both clocks: "G <mach s> ... us=<steady us>").
For every shown present: the gfx kick (TL code 5) whose send_dl (code 8) produced its workload (last W before its Q), and that
kick's chain: kick gap from the previous kick, kick phase after the VI edge before it, q (kick->task start), rsp (task start->
RSP exit), rdp (RSP exit->send_dl return), and the game thread's (osViSwapBuffer slot) blocked/running ms between the two kicks
split by mq. Single-vsync-late presents (P->P 30-40 ms) vs normal (15-18.5 ms).
usage: g1e_tl_present.py tl.bin.<pid> gring.txt ring.txt [--from S]"""
import sys, struct, bisect, collections, statistics as st
args = sys.argv[1:]; t_from = 60.0
if '--from' in args: i = args.index('--from'); t_from = float(args[i + 1]); del args[i:i + 2]
tlf, gf, rf = args
pc = lambda v, p: sorted(v)[int(p * (len(v) - 1))] if v else float('nan')
off = []
for l in open(gf, errors='replace'):
    if l.startswith('G ') and ' us=' in l and l.endswith('\n'):
        p = l.split(); us = int(next(x for x in p if x.startswith('us='))[3:]); off.append(float(p[1]) - us / 1e6)
if not off: sys.exit('no us= in G rows')
o = st.median(off); spread = (max(off) - min(off)) * 1e3
print(f'clock offset mach-steady {o:.6f} s, spread {spread:.3f} ms over {len(off)} G rows (positive control: < 1 ms)')
raw = open(tlf, 'rb').read(); n = len(raw) // 24
ev = sorted((lambda r: (r[0] / 1e6 + o, r[1], r[2], r[4]))(struct.unpack_from('<qIIii', raw, i * 24)) for i in range(n))
ev = [e for e in ev if e[0] > o + 1]
t0 = ev[0][0]
G = collections.Counter(e[3] for e in ev if e[1] == 15).most_common(1)[0][0]
vis = [e[0] for e in ev if e[1] == 1]
kicks = [i for i, e in enumerate(ev) if e[1] == 5 and e[2] == 1]; kt = [ev[i][0] for i in kicks]
sdret = [e[0] for e in ev if e[1] == 8]
Q = {}; P = []; W = []
for l in open(rf, errors='replace'):
    p = l.split()
    if len(p) < 3 or not l.endswith('\n'): continue
    kv = dict(x.split('=', 1) for x in p[2:] if '=' in x)
    try:
        if p[0] == 'Q' and kv.get('skip') == '0' and 'acq_ms' in kv: Q[int(kv['mtl'])] = float(p[1])
        elif p[0] == 'P' and float(kv.get('at', 0)) > 0: P.append((float(kv['at']), int(kv['mtl'])))
        elif p[0] == 'W': W.append(float(p[1]))
    except (KeyError, ValueError): pass
P.sort(); W.sort()
RR = sorted((float(l.split()[1]), float(l.split()[2][3:]), float(l.split()[3][4:]), float(l.split()[4][3:])) for l in open(gf, errors='replace') if l.startswith('R ') and ' sdc=' in l and l.endswith('\n'))
Rt = [r[0] for r in RR]
def rrow(w):
    j = bisect.bisect_left(Rt, w) - 1  # the send_dl that returned last before W (W follows it; next R is the next frame)
    return RR[j] if j >= 0 and w - RR[j][0] < 0.05 else None
# positive control 2: every W should sit inside a kick -> send_dl-return window
inwin = 0; tot = 0
for w in W:
    if w - t0 < t_from: continue
    k = bisect.bisect_right(kt, w) - 1; s = bisect.bisect_left(sdret, w)
    tot += 1; inwin += (k >= 0 and s < len(sdret) and sdret[s] >= kt[k] and (s == 0 or sdret[s - 1] < kt[k]) is not None and sdret[s] - w < 0.05)
print(f'W rows within 50 ms before a send_dl return: {inwin}/{tot}')
def chain(k):
    i, j = kicks[k], kicks[k + 1] if k + 1 < len(kicks) else len(ev) - 1
    def nxt(a, code, lim):
        for x in range(a + 1, lim):
            if ev[x][1] == code: return x
        return None
    ts = nxt(i, 6, j + 400); rx = nxt(ts, 7, j + 400) if ts else None; sd = nxt(ts, 8, j + 400) if ts else None
    gap = (ev[i][0] - ev[kicks[k - 1]][0]) * 1e3 if k > 0 else float('nan')
    p = bisect.bisect_right(vis, ev[i][0]) - 1; ph = (ev[i][0] - vis[p]) * 1e3 if p >= 0 else float('nan')
    # game thread between previous kick and this one: blocked per mq, running
    a0 = kicks[k - 1] if k > 0 else i; b = collections.Counter(); op = None
    for x in range(a0, i):
        e = ev[x]
        if e[3] != G: continue
        if e[1] == 10: op = (e[2], e[0])
        elif e[1] == 11 and op and op[0] == e[2]: b[e[2]] += (e[0] - op[1]) * 1e3; op = None
    if op: b[op[0]] += (ev[i][0] - op[1]) * 1e3
    # previous kick's own gfx chain (the gfx thread may still be busy with it)
    return dict(gap=gap, ph=ph, q=(ev[ts][0] - ev[i][0]) * 1e3 if ts else float('nan'),
                rsp=(ev[rx][0] - ev[ts][0]) * 1e3 if rx and ts else float('nan'), rdp=(ev[sd][0] - ev[rx][0]) * 1e3 if sd and rx else float('nan'),
                run=gap - sum(b.values()), blk=b, nvi=bisect.bisect_right(vis, ev[i][0]) - bisect.bisect_right(vis, ev[a0][0]))
rows = {'late': [], 'norm': []}
for j in range(1, len(P)):
    d = (P[j][0] - P[j - 1][0]) * 1e3; m = P[j][1]
    if m not in Q or P[j][0] - t0 < t_from: continue
    i = bisect.bisect_right(W, Q[m])
    if i < 1: continue
    k = bisect.bisect_right(kt, W[i - 1]) - 1
    if k < 1: continue
    c = chain(k); c['prev'] = chain(k - 1); c['wq'] = (Q[m] - W[i - 1]) * 1e3; c['kw'] = (W[i - 1] - kt[k]) * 1e3; c['t'] = P[j][0] - t0; r = rrow(W[i - 1]); c['sd'], c['sdc'], c['qw'], c['rw'] = (r[1], r[2], r[3], (r[0] - W[i - 1]) * 1e3) if r else (float('nan'),) * 4; c['pre'] = c['sd'] - c['sdc']
    if 30 <= d < 40: rows['late'].append(c)
    elif 15 < d < 18.5: rows['norm'].append(c)
L, N = rows['late'], rows['norm']
print(f'game slot {G}; late presents {len(L)}, normal {len(N)}')
print('  field           late p10/p50/p90          | normal p10/p50/p90')
for k in ('gap', 'ph', 'nvi', 'run', 'q', 'rsp', 'rdp', 'kw', 'wq', 'sd', 'sdc', 'pre', 'qw', 'rw'):
    print('  %-6s %8.2f %8.2f %8.2f          | %8.2f %8.2f %8.2f' % (k, *(pc([r[k] for r in L], x) for x in (.1, .5, .9)), *(pc([r[k] for r in N], x) for x in (.1, .5, .9))))
for k in ('gap', 'ph', 'rsp', 'rdp', 'run'):
    print('  prev.%-4s %8.2f %8.2f %8.2f          | %8.2f %8.2f %8.2f' % (k, *(pc([r['prev'][k] for r in L], x) for x in (.1, .5, .9)), *(pc([r['prev'][k] for r in N], x) for x in (.1, .5, .9))))
for nm, R in (('late', L), ('normal', N)):
    mq = collections.Counter()
    for r in R: mq.update(r['blk'])
    print(f'  {nm}: game blocked ms per kick interval by mq: ' + ', '.join(f'0x{m:08X} {v / max(1, len(R)):.2f}' for m, v in mq.most_common(4)))
print('  per late present: t s | ph | rsp | sd wall | sdc cpu | wall-cpu | VI-ack blk | verdict')
nph = pc([r['ph'] for r in N], .99); nrsp = pc([r['rsp'] for r in N], .99); npre = pc([r['pre'] for r in N], .99); ncpu = pc([r['sdc'] for r in N], .99)
print(f'  normal p99: ph {nph:.2f} rsp {nrsp:.2f} wall-cpu {npre:.2f} cpu {ncpu:.2f}')
for r in L:
    v = []
    if r['ph'] > nph: v.append('H-sched')
    if r['rsp'] > nrsp: v.append('H-rsp-host' if r['pre'] > npre else ('H-rsp-work' if r['sdc'] > ncpu else 'H-rsp-?'))
    print('  %7.2f | %5.2f | %5.2f | %6.2f | %6.2f | %6.2f | %5.2f | %s' % (r['t'], r['ph'], r['rsp'], r['sd'], r['sdc'], r['pre'], r['blk'].get(0x80128CF0, 0), '+'.join(v) or 'none>p99'))
