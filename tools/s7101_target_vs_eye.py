#!/usr/bin/env python3
"""s7101 fps60-wall-camera: is the eye zig-zag at a near-wall flicker episode made by the chase camera itself, or is it
inherited from the craft it chases?

s7101 static read: the flight camera position (cam = *0x80138D1C = 0x80138458, translation +0x4C..+0x54) is written once
per tick by updatePlayerVehicleByControlMode (0x8004D7E0..EC, or 0x8004D680..88 / 0x8004D7F4.. on its other branches).
It is a pure chase: pos += speed*dt*unit(target - pos), target = craft matrix x offset (cam+0x58); speed is rate limited.
No terrain or wall query. So the camera cannot 'push out' of a wall by itself; a tick-by-tick reversal of the eye must
come either from the chase step (H-chase: speed*dt overshoots the target) or from the craft (H-craft: the craft position
reverses tick by tick, e.g. the terrain-scrape deflection at 60 Hz).

Inputs per run: the game log with s7099 [g3c] lines (eye=, pl= : pl fields 1..3 are the craft position), the g5b_drops
csv, and the soak result (lim=N ... times [...]). Same windows and episode rule as tools/s7100_episode_eye.py.
Per window: eye reversals, craft reversals, and ticks where both reverse on the same tick. Baseline: all flight windows.
H-craft predicts craft reversals >= eye reversals in episode windows with most eye reversals coinciding with craft ones;
H-chase predicts eye reversals with a smooth craft.
usage: s7101_target_vs_eye.py game.log drops.csv soak_res.log [--pre 0.3] [--post 0.1]"""
import sys, re, math, bisect, ast
a = sys.argv[1:]; PRE, POST = 0.3, 0.1
def opt(name):
    global a
    if name in a:
        i = a.index(name); v = float(a[i + 1]); del a[i:i + 2]; return v
PRE = opt('--pre') or PRE; POST = opt('--post') or POST
glog, dcsv, res = a[:3]
times = {}
for l in open(res, errors='replace'):
    g = re.match(r'lim=(\d+) span .* times (\[.*\])', l)
    if g: times[int(g.group(1))] = ast.literal_eval(g.group(2))
num = r'([-\d.e+]+)'
rx = re.compile(r'\[g3c\] vi=\d+ t=[\d.]+ tasks=\d+ lim=(\d+) m=(\d+) eye=' + ','.join([num] * 3) + r' cam=\S+ pl=' + ','.join([num] * 4))
M, L, E, P = [], [], [], []
for l in open(glog, errors='replace'):
    g = rx.search(l)
    if not g: continue
    e = tuple(float(g.group(k)) for k in (3, 4, 5))
    if E and e == E[-1]: continue
    M.append(int(g.group(2))); L.append(int(g.group(1))); E.append(e); P.append(tuple(float(g.group(k)) for k in (7, 8, 9)))
rows = [l.split(',') for l in open(dcsv)][1:]
cap0 = int(rows[0][6]) - float(rows[0][1]) * 24e6
def revs(seq, i0, i1):
    st = [[seq[i][k] - seq[i - 1][k] for k in range(3)] for i in range(max(i0, 1), i1)]
    out = set()
    for j in range(1, len(st)):
        if sum(st[j][k] * st[j - 1][k] for k in range(3)) < 0: out.add(j)
    return out, st
def stats(m0, m1):
    i0 = bisect.bisect_left(M, m0); i1 = bisect.bisect_right(M, m1)
    er, es = revs(E, i0, i1); pr, ps = revs(P, i0, i1)
    mv = all(math.dist(P[i], P[i - 1]) > 1e-3 for i in range(max(i0, 1), i1))
    # eye/craft step ratio (eye is in terrain units: compare shapes only via reversals)
    return dict(n=len(es), er=len(er), pr=len(pr), both=len(er & pr), moving=mv, lim=L[i0] if i0 < len(L) else -1)
tot = {}
for lim, ts in sorted(times.items()):
    ep = [t for i, t in enumerate(ts) if i == 0 or t - ts[i - 1] > 1.0]
    for t in ep:
        m = cap0 + t * 24e6; s = stats(m - PRE * 24e6, m + POST * 24e6)
        print('EP lim=%d t=%.1f ticks %d eye_rev %d craft_rev %d same_tick %d' % (lim, t, s['n'], s['er'], s['pr'], s['both']))
        T = tot.setdefault(lim, [0, 0, 0, 0, 0]); T[0] += 1; T[1] += s['n']; T[2] += s['er']; T[3] += s['pr']; T[4] += s['both']
for k, T in sorted(tot.items()):
    print('EPSUM lim=%d episodes %d ticks %d eye_rev %d craft_rev %d same_tick %d' % (k, *T))
W = int((PRE + POST) * 24e6); lo = cap0 + 5 * 24e6; hi = cap0 + float(rows[-1][1]) * 24e6; base = {}
m = lo
while m + W < hi:
    s = stats(m, m + W)
    if s['moving'] and s['n'] >= 3:
        b = base.setdefault(s['lim'], [0, 0, 0, 0, 0]); b[0] += 1; b[1] += s['n']; b[2] += s['er']; b[3] += s['pr']; b[4] += s['both']
    m += W
for k, b in sorted(base.items()):
    print('BASE lim=%d windows %d ticks %d eye_rev/tick %.4f craft_rev/tick %.4f same/tick %.4f' % (k, b[0], b[1], b[2] / b[1], b[3] / b[1], b[4] / b[1]))
