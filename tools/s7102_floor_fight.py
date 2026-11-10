#!/usr/bin/env python3
"""s7102 fps60-wall-camera: does the applyPlayerVehicleStateUpdate y-floor clamp (0x8004CFD4..0x8004D04C) fight the corner
push-out tick by tick? Per flight-camera tick (s7102 pu/yf/pe lines): push = any corner hit, yfd = pe.y - y before the clamp
(last pu post), flip = an all-miss tick between two push ticks. Per lim (last ch line) and in/out of the episode windows.
usage: s7102_floor_fight.py push.txt drops.csv split.txt"""
import sys, re, ast, bisect
pf, dcsv, spl = sys.argv[1:4]
V = lambda s: tuple(map(float, s.split(',')))
T = []; cur = None; lim = 0
for l in open(pf, errors='replace'):
    d = dict(re.findall(r'(\w+)=(\S+)', l)); k = l[:2]
    if d.get('cam') != '80138458': continue
    try:
        if k == 'ch' and 'off' in d: lim = int(d['lim'])
        elif k == 'pu':
            if cur is None: cur = {'hit': 0, 'y0': None, 'yf': 0}
            cur['hit'] |= int(d['hit']); cur['y0'] = V(d['post'])[1]
        elif k == 'yf' and cur: cur['yf'] = 1
        elif k == 'pe':
            if cur and cur['y0'] is not None:
                T.append((int(d['m']), lim, cur['hit'], cur['yf'], V(d['pos'])[1] - cur['y0']))
            cur = None
    except (ValueError, KeyError):
        cur = None
rows = [l.split(',') for l in open(dcsv)][1:]
cap0 = int(rows[0][6]) - float(rows[0][1]) * 24e6
ep = []
for l in open(spl, errors='replace'):
    g = re.match(r'lim=(\d+) span .* times (\[.*\])', l)
    if g:
        ts = ast.literal_eval(g.group(2)); ep += [cap0 + x * 24e6 for i, x in enumerate(ts) if i == 0 or x - ts[i - 1] > 1.0]
inep = lambda m: any(e - 0.3 * 24e6 <= m <= e + 0.1 * 24e6 for e in ep)
print('ticks %d episodes %d' % (len(T), len(ep)))
print('set       lim ticks push%%  yf%%  |yfd|>0.1%%  yfd<-0.1%%  flips/1000')
for name, sel in (('episode', lambda t: inep(t[0])), ('flight', lambda t: not inep(t[0]))):
    for L in (1, 2):
        S = [t for t in T if t[1] == L and sel(t)]
        if not S: continue
        fl = sum(1 for i in range(1, len(S) - 1) if S[i][2] == 0 and S[i - 1][2] and S[i + 1][2])
        n = len(S)
        print('%-8s  %d  %5d  %5.1f  %5.1f  %6.2f  %6.2f  %7.2f' % (name, L, n, 100. * sum(t[2] for t in S) / n, 100. * sum(t[3] for t in S) / n,
              100. * sum(abs(t[4]) > 0.1 for t in S) / n, 100. * sum(t[4] < -0.1 for t in S) / n, 1000. * fl / n))
