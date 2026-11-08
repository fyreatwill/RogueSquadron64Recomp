#!/usr/bin/env python3
"""s6967 G1e: split game-frame intervals from a ROGUESQ_G1E_GRING ring (G/R rows) and join them to a present ring.
usage: g1e_gring.py gring.txt [present_ring.txt] [--from S]
Per interval between consecutive gfx task submits (G rows) of the submitting guest thread:
  wall = G gap, cpu = its CPU delta, blk = its blocked-in-osRecvMesg delta, rest = wall-cpu-blk (runnable, not running),
  oth = CPU of all other guest threads in the interval (top one named), sd/qw = send_dl wall and queue wait of the task.
Compares long intervals (>=20 ms) against normal (14-19 ms), then (with a present ring) the interval that produced each
single-vsync-late present (P->P 30-40 ms) against the one behind normal presents (15-18.5 ms)."""
import sys, bisect, collections
pc = lambda v, p: sorted(v)[int(p * (len(v) - 1))] if v else float('nan')
args = [a for a in sys.argv[1:]]
t_from = 0.0
if '--from' in args:
    i = args.index('--from'); t_from = float(args[i + 1]); del args[i:i + 2]
G = []; R = []
for l in open(args[0], errors='replace'):
    if not l.endswith('\n'): continue
    p = l.split()
    try:
        if p[0] == 'G':
            sl = {}
            for x in p[3:]:
                if x.startswith(('sl=', 'us=')): continue
                k, v = x.split(':'); c, b = v.split('/'); sl[k] = (float(c), float(b))
            G.append((float(p[1]), int(p[2][3:]), sl))
        elif p[0] == 'R':
            kv = dict(x.split('=') for x in p[2:]); R.append((float(p[1]), float(kv['sd']), float(kv['qw'])))
    except (ValueError, IndexError, KeyError):
        pass
if not G: sys.exit('no G rows')
t0 = G[0][0]
G = [g for g in G if g[0] - t0 >= t_from]
os_main = collections.Counter(g[1] for g in G).most_common(1)[0][0]
G = [g for g in G if g[1] == os_main]
cand = [k for k in G[-1][2] if k.split('.')[1] == str(os_main) and k in G[0][2]]
key = max(cand, key=lambda k: G[-1][2][k][0] - G[0][2][k][0])  # several slots can share an osid: take the busiest
Rt = [r[0] for r in R]
iv = []
for a, b in zip(G, G[1:]):
    if key not in a[2] or key not in b[2]: continue
    w = (b[0] - a[0]) * 1e3
    c = b[2][key][0] - a[2][key][0]; bl = b[2][key][1] - a[2][key][1]
    oth = {k: b[2][k][0] - a[2][k][0] for k in b[2] if k != key and k in a[2]}
    top = max(oth.items(), key=lambda kv: kv[1]) if oth else ('-', 0.0)
    j = bisect.bisect_left(Rt, b[0])  # the send_dl of task b ends after b's submit
    sd, qw = (R[j][1], R[j][2]) if j < len(R) else (float('nan'), float('nan'))
    iv.append(dict(t=b[0], wall=w, cpu=c, blk=bl, rest=w - c - bl, oth=sum(oth.values()), top=top[0], topc=top[1], sd=sd, qw=qw))
print('%s: game thread os=%d slot %s, %d intervals, wall p50 %.2f ms' % (args[0], os_main, key, len(iv), pc([x['wall'] for x in iv], .5)))
F = ['wall', 'cpu', 'blk', 'rest', 'oth', 'topc', 'sd', 'qw']
def table(name_a, A, name_b, B):
    print('  %-5s %-28s | %s' % ('', '%s n=%d p10/p50/p90' % (name_a, len(A)), '%s n=%d p10/p50/p90' % (name_b, len(B))))
    for k in F:
        print('  %-5s %8.2f %8.2f %8.2f    | %8.2f %8.2f %8.2f' % (k, *(pc([x[k] for x in A], q) for q in (.1, .5, .9)), *(pc([x[k] for x in B], q) for q in (.1, .5, .9))))
    tops = collections.Counter(x['top'] for x in A).most_common(3)
    print('  top other thread in %s: %s' % (name_a, tops))
long_ = [x for x in iv if x['wall'] >= 20]; norm = [x for x in iv if 14 <= x['wall'] < 19]
print(' intervals >=20 ms: %d (%.2f/s)' % (len(long_), len(long_) / max(1e-9, iv[-1]['t'] - iv[0]['t'])))
table('long', long_, 'normal', norm)
# excess attribution on long intervals: which term carries (wall - 16.7)
if long_:
    mn = {k: pc([x[k] for x in norm], .5) for k in ('cpu', 'blk', 'rest')}
    ex = collections.Counter()
    for x in long_:
        d = {k: x[k] - mn[k] for k in ('cpu', 'blk', 'rest')}
        ex[max(d, key=d.get)] += 1
    print('  term with the largest excess over the normal median, per long interval:', dict(ex))
if len(args) > 1:
    Q = {}; P = []; W = []
    for l in open(args[1], errors='replace'):
        p = l.split()
        if len(p) < 3 or not l.endswith('\n'): continue
        kv = dict(x.split('=', 1) for x in p[2:] if '=' in x)
        try:
            if p[0] == 'Q' and kv.get('skip') == '0' and 'acq_ms' in kv: Q[int(kv['mtl'])] = float(p[1])
            elif p[0] == 'P' and float(kv.get('at', 0)) > 0: P.append((float(kv['at']), int(kv['mtl'])))
            elif p[0] == 'W': W.append(float(p[1]))
        except (KeyError, ValueError):
            pass
    P.sort(); W.sort(); It = [x['t'] for x in iv]
    rows = {'miss': [], 'norm': []}
    for j in range(1, len(P)):
        d = (P[j][0] - P[j - 1][0]) * 1e3; m = P[j][1]
        if m not in Q or P[j][0] - t0 < t_from: continue
        i = bisect.bisect_right(W, Q[m])
        if i < 1: continue
        k = bisect.bisect_right(It, W[i - 1]) - 1  # last game submit before that workload
        if k < 0: continue
        if 30 <= d < 40: rows['miss'].append(iv[k])
        elif 15 < d < 18.5: rows['norm'].append(iv[k])
    print(' present join: single-vsync-late presents %d, normal %d' % (len(rows['miss']), len(rows['norm'])))
    table('late', rows['miss'], 'normal', rows['norm'])
    print('  late presents whose producing interval was >=20 ms: %d/%d' % (sum(x['wall'] >= 20 for x in rows['miss']), len(rows['miss'])))
