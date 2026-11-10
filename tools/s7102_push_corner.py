#!/usr/bin/env python3
"""s7102 fps60-wall-camera: near-plane push-out per corner at near-wall flicker episodes, and the CAM4 (4-corner) arm split.
Input: the ROGUESQ_S7101_CHASE file carrying s7101 ch lines and s7102 pu/pc/yf/pe lines (tools/apply_s7102_pushlog.py),
the g5b_drops csv and the s7099_wall_split output (lim=N ... times [...]) of the same run.
A tick = the pu/pc/yf lines of the flight camera up to its pe line. Per tick: hit mask over corners 0-3 (corner 3 from the
real test when cam4=1, else from the scratch probe pc), yf, |pe - pre| push length, lim (last ch line).
Reports:
  control: pe pos == next ch pre-step pos (same cam), hits > 0
  per (cam4, lim): ticks, ticks with any push, corner-3-only-inside ticks (c3 hit, 0-2 clear), episodes, episodes/1000 ticks
  per episode window (-PRE..+POST s): tick strings of hit masks ('0123' digits that hit, '.' none) + c3-only count + yf count
usage: s7102_push_corner.py push.txt drops.csv split.txt [--pre 0.3] [--post 0.1]"""
import sys, re, ast, bisect
from collections import Counter, defaultdict
a = sys.argv[1:]; PRE, POST = 0.3, 0.1
if '--pre' in a: i = a.index('--pre'); PRE = float(a[i + 1]); del a[i:i + 2]
if '--post' in a: i = a.index('--post'); POST = float(a[i + 1]); del a[i:i + 2]
pf, dcsv, spl = a[:3]
V = lambda s: tuple(map(float, s.split(',')))
ticks = []; cur = None; lim = 0; chs = []; flightcam = Counter()
for l in open(pf, errors='replace'):
    d = dict(re.findall(r'(\w+)=(\S+)', l)); k = l[:2]
    try:
        if k == 'ch' and 'off' in d:
            lim = int(d['lim']); chs.append((int(d['m']), d['cam'], V(d['pos']))); flightcam[d['cam']] += 1
        elif k == 'pu':
            if cur is None or cur['cam'] != d['cam']: cur = {'cam': d['cam'], 'hits': {}, 'pre': None, 'yf': 0, 'p3': None}
            i = int(d['i']); cur['hits'][i] = int(d['hit']) != 0
            if i == 0: cur['pre'] = V(d['pre'])
        elif k == 'pc' and cur is not None and cur['cam'] == d['cam']:
            cur['p3'] = int(d['hit']) != 0
        elif k == 'yf' and cur is not None and cur['cam'] == d['cam']:
            cur['yf'] = 1
        elif k == 'pe':
            if cur is not None and cur['cam'] == d['cam'] and cur['pre'] is not None:
                cur.update(m=int(d['m']), cam4=int(d['cam4']), pos=V(d['pos']), lim=lim)
                if cur['cam4']: cur['p3'] = cur['hits'].get(3, False)
                ticks.append(cur)
            cur = None
    except (ValueError, KeyError):
        cur = None
fc = flightcam.most_common(1)[0][0] if flightcam else None
ticks = [t for t in ticks if t['cam'] == fc]
print('flight cam %s ticks %d ch %d' % (fc, len(ticks), len(chs)))
# control: final pos of a push-out tick == pre-step pos of the next ch line of the same cam
CM = [c[0] for c in chs if c[1] == fc]; CP = [c[2] for c in chs if c[1] == fc]
ok = bad = 0
for t in ticks:
    j = bisect.bisect_right(CM, t['m'])
    if j < len(CM):
        if max(abs(CP[j][q] - t['pos'][q]) for q in range(3)) < 1e-4: ok += 1
        else: bad += 1
nh = sum(1 for t in ticks if any(t['hits'].values()))
print('control: pe==next ch pos %d / %d; ticks with a hit %d; yf ticks %d' % (ok, ok + bad, nh, sum(t['yf'] for t in ticks)))
def mask(t):
    s = ''.join(str(i) for i in range(3) if t['hits'].get(i)) + ('3' if t['p3'] else '')
    return s or '.'
def c3only(t): return bool(t['p3']) and not any(t['hits'].get(i) for i in range(3))
rows = [l.split(',') for l in open(dcsv)][1:]
cap0 = int(rows[0][6]) - float(rows[0][1]) * 24e6
eps = defaultdict(list)
for l in open(spl, errors='replace'):
    g = re.match(r'lim=(\d+) span .* times (\[.*\])', l)
    if g:
        ts = ast.literal_eval(g.group(2))
        eps[int(g.group(1))] += [x for i, x in enumerate(ts) if i == 0 or x - ts[i - 1] > 1.0]
TM = [t['m'] for t in ticks]
def at(m):
    j = min(max(bisect.bisect_left(TM, m), 0), len(TM) - 1); return ticks[j]
epc = Counter(); epw = []
for L in sorted(eps):
    for x in sorted(eps[L]):
        m = cap0 + x * 24e6; t = at(m); epc[(t['cam4'], L)] += 1
        i0 = bisect.bisect_left(TM, m - PRE * 24e6); i1 = bisect.bisect_right(TM, m + POST * 24e6)
        W = ticks[i0:i1]
        epw.append((L, x, t['cam4'], W))
inep = set()
for _, _, _, W in epw:
    for t in W: inep.add(id(t))
print('\ncam4 lim ticks push%% c3only%% c3only_ticks episodes ep/1000t')
for c4 in (0, 1):
    for L in (1, 2):
        T = [t for t in ticks if t['cam4'] == c4 and t['lim'] == L]
        if not T: continue
        p = sum(1 for t in T if any(t['hits'].values()) or (c4 and t['p3'])); c3 = sum(1 for t in T if c3only(t))
        print('%d    %d  %6d  %5.1f  %5.2f  %5d  %3d  %.3f' % (c4, L, len(T), 100.0 * p / len(T), 100.0 * c3 / len(T), c3, epc[(c4, L)], 1000.0 * epc[(c4, L)] / len(T)))
B = [t for t in ticks if id(t) not in inep and t['cam4'] == 0]
if B:
    print('baseline (cam4=0, not in episodes): ticks %d c3only %.2f%% any-push %.1f%%' % (len(B), 100.0 * sum(map(c3only, B)) / len(B),
          100.0 * sum(1 for t in B if any(t['hits'].values())) / len(B)))
print('\nepisodes (mask per tick: corner digits that hit, 3 = corner 3 inside; | marks the episode time)')
for L, x, c4, W in epw:
    m = cap0 + x * 24e6
    s = ''.join(('|' if (i > 0 and W[i - 1]['m'] < m <= w['m']) else '') + '[' + mask(w) + ']' for i, w in enumerate(W))
    print('lim=%d t=%.1f cam4=%d ticks %d c3only %d yf %d push-ticks %d  %s' % (L, x, c4, len(W), sum(map(c3only, W)), sum(w['yf'] for w in W),
          sum(1 for w in W if any(w['hits'].values())), s[:400]))
