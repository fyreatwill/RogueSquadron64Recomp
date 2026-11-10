#!/usr/bin/env python3
"""s7100 fps60-wall-camera: classify the camera-eye (0x80130C10) motion around every near-wall flicker episode, against a
baseline of all same-length flight windows in the same arbiter state (lim 1 = 60 fps window, 2 = retail 30).
Inputs: the game log with s7099 [g3c] lines (lim=, m=, eye=, pl=), the g5b_drops csv (mach column = capture clock), and the
episode event times in capture seconds (the `times [...]` list s7099_wall_split.py prints; pass the soak's result log with
--res and the times are parsed from it).
Per window [-PRE, +POST] s around the first event of an episode: ticks (eye changes), reversals (consecutive eye steps with a
negative dot product while the craft moves), stops (step < 0.25x the window's median step), class:
  jitter >=2 reversals, stop >=1 reversal or stop, smooth otherwise.
Baseline: the same statistic over every window start t0..t1 stepping by PRE+POST, per lim, flight only (craft moving).
H-push predicts episode windows are jitter/stop far above baseline, and in lim=1 more than lim=2.
usage: s7100_episode_eye.py game.log drops.csv (--res soak.log | t1,t2,...) [--pre 0.3] [--post 0.1]"""
import sys, re, math, bisect, ast
a = sys.argv[1:]; PRE, POST = 0.3, 0.1
def opt(name, conv):
    global a
    if name in a:
        i = a.index(name); v = conv(a[i + 1]); del a[i:i + 2]; return v
PRE = opt('--pre', float) or PRE; POST = opt('--post', float) or POST
res = opt('--res', str)
glog, dcsv = a[:2]
times = {}  # lim -> list of event times
if res:
    for l in open(res, errors='replace'):
        g = re.match(r'lim=(\d+) span .* times (\[.*\])', l)
        if g: times[int(g.group(1))] = ast.literal_eval(g.group(2))
else:
    times[0] = [float(x) for x in a[2].split(',')]
rx = re.compile(r'\[g3c\] vi=(\d+) t=([\d.]+) tasks=(\d+) lim=(\d+) m=(\d+) eye=([-\d.e+]+),([-\d.e+]+),([-\d.e+]+) cam=\S+ pl=([-\d.e+]+),([-\d.e+]+),([-\d.e+]+)')
M, L, E, P = [], [], [], []
for l in open(glog, errors='replace'):
    g = rx.search(l)
    if not g: continue
    e = tuple(float(g.group(k)) for k in (6, 7, 8))
    if E and e == E[-1]: continue  # keep new ticks only
    M.append(int(g.group(5))); L.append(int(g.group(4))); E.append(e); P.append(tuple(float(g.group(k)) for k in (9, 10, 11)))
rows = [l.split(',') for l in open(dcsv)][1:]
cap0 = int(rows[0][6]) - float(rows[0][1]) * 24e6  # capture t=0 on the mach clock
def stats(m0, m1):
    i0 = bisect.bisect_left(M, m0); i1 = bisect.bisect_right(M, m1)
    steps, rev, mv = [], 0, True
    for i in range(max(i0, 1), i1):
        s = [E[i][k] - E[i - 1][k] for k in range(3)]; steps.append(s)
        if math.dist(P[i], P[i - 1]) < 1e-3: mv = False
    for j in range(1, len(steps)):
        if sum(steps[j][k] * steps[j - 1][k] for k in range(3)) < 0: rev += 1
    mag = sorted(math.sqrt(sum(v * v for v in s)) for s in steps)
    med = mag[len(mag) // 2] if mag else 0
    stop = sum(1 for x in mag if x < 0.25 * med) if med else 0
    cls = 'jitter' if rev >= 2 else ('stop' if rev or stop else 'smooth')
    lim = L[i0] if i0 < len(L) else -1
    return dict(n=len(steps), rev=rev, stop=stop, cls=cls, moving=mv, lim=lim, med=med)
W = int((PRE + POST) * 24e6)
for lim, ts in sorted(times.items()):
    ep = [t for i, t in enumerate(ts) if i == 0 or t - ts[i - 1] > 1.0]
    for t in ep:
        m = cap0 + t * 24e6; s = stats(m - PRE * 24e6, m + POST * 24e6)
        print('EP lim=%d t=%.1f ticks %d rev %d stop %d med %.3f moving %d -> %s' % (lim, t, s['n'], s['rev'], s['stop'], s['med'], s['moving'], s['cls']))
# baseline over the capture span (flight), per lim
lo = cap0 + 5 * 24e6; hi = cap0 + float(rows[-1][1]) * 24e6
base = {}
m = lo
while m + W < hi:
    s = stats(m, m + W)
    if s['moving'] and s['n'] >= 3:
        b = base.setdefault(s['lim'], {'jitter': 0, 'stop': 0, 'smooth': 0}); b[s['cls']] += 1
    m += W
for k in sorted(base):
    b = base[k]; n = sum(b.values())
    print('BASE lim=%d windows %d jitter %.3f stop %.3f smooth %.3f' % (k, n, b['jitter'] / n, b['stop'] / n, b['smooth'] / n))
