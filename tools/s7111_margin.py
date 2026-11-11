#!/usr/bin/env python3
"""s7111 fps60-wall-margin: offline split of the eye-cell near-z losses into H-postmove / H-probe / H-pushed, from one
ROGUESQ_S7101_CHASE log (ch/pu/pc/rx/pe/bv lines, s7101/s7102/s7103 patches) + the s7107 losscan rows + the drops csv clock.

Per flight-camera tick (cam of the ch lines): pe = pushed pos at push-out exit; bv = the eye the terrain builder reads from the
camera matrix translation (+0x4C); pu = per-corner ray tests (hit flag, hit point, pre/post pos, f20 = 2*near margin).
Per tick metrics: dmv = |bv - last pe before it| (eye moved after the push?), pushed = any pu hit this tick, mind = min over hit
corners of |hp - pre| (wall distance along that corner ray, game units), rx residual mask.
Each eye-cell near-z loss (ref painter c+0+0, drop near minz < 0x100, t >= 0) is joined to the ticks in [t-WIN, t] (camera ticks
that can have fed the dropped swap). Control: the same metrics over every flight tick (base rates).
usage: s7111_margin.py chase.txt drops.csv losscan.txt [WIN=0.15]"""
import sys, re, math, collections
chase, dcsv, lsc = sys.argv[1:4]; WIN = float(sys.argv[4]) if len(sys.argv) > 4 else 0.15
FC = '80138458'
rows = [l.strip().split(',') for l in open(dcsv)][1:]
ec = sorted((int(p[6]), float(p[1])) for p in rows); lcap0 = ec[0][0] - ec[0][1] * 24e6
rl = re.compile(r'sw\s+(\d+) t=\s*([-\d.]+) lost\s+(\d+) ref (\[.*?\]) -> .*near tris/minz ref (\d+)/([0-9A-F]+) drop (\d+)/([0-9A-F]+)')
eye, other = [], []
for line in open(lsc):
    g = rl.search(line)
    if not g or float(g.group(2)) < 0: continue
    m = lcap0 + float(g.group(2)) * 24e6
    (eye if "'c+0+0'" in g.group(4).split(',')[0] and int(g.group(8), 16) < 0x100 else other).append((m, float(g.group(2)), int(g.group(6), 16), int(g.group(8), 16)))
V = lambda s: [float(x) for x in s.split(',')]
ticks = []; cur = None; lastpe = None
kv = re.compile(r'(\w+)=(\S+)')
for line in open(chase, errors='replace'):
    k = line[:2]
    if k not in ('pu', 'rx', 'pe', 'bv', 'ch'): continue
    d = dict(kv.findall(line))
    if d.get('cam') != FC: continue
    m = int(d['m'])
    if k == 'ch':
        cur = {'m': m, 'pu': [], 'rx': None, 'pe': None, 'bv': [], 'ch': V(d['pos']), 'tgt': V(d['tgt'])}; ticks.append(cur)
    elif cur is None: continue
    elif k == 'pu': cur['pu'].append((int(d['i']), int(d['hit']), V(d['hp']), V(d['pre']), V(d['post']), float(d['f20']), V(d['c'])))
    elif k == 'rx': cur['rx'] = (int(d['r']), int(d['f']), int(d['yc']), V(d['p0']), V(d['pos']), int(d['fx']), int(d['np']))
    elif k == 'pe': cur['pe'] = V(d['pos']); lastpe = cur['pe']
    elif k == 'bv': cur['bv'].append((m, V(d['rd']), lastpe))
dist = lambda a, b: math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
def met(t):
    hits = [p for p in t['pu'] if p[1]]
    mind = min((dist(p[2], p[3]) for p in hits), default=None)
    mv = max((dist(b[1], b[2]) for b in t['bv'] if b[2]), default=None)
    pmv = dist(t['pe'], t['pu'][0][3]) if t['pe'] and t['pu'] else 0.0
    f20 = t['pu'][0][5] if t['pu'] else None
    return dict(fx=t['rx'][5] if t['rx'] else -1, f=t['rx'][1] if t['rx'] else -1, np=t['rx'][6] if t['rx'] else 0, nh=len(hits), mind=mind, mv=mv, pmv=pmv, r=t['rx'][0] if t['rx'] else -1, yc=t['rx'][2] if t['rx'] else -2, f20=f20)
M = [met(t) for t in ticks]
def summ(idx, name):
    n = len(idx)
    if not n: print(name, 'n=0'); return
    pushed = sum(1 for i in idx if M[i]['nh']); res = sum(1 for i in idx if M[i]['r'] > 0); yc = sum(1 for i in idx if M[i]['yc'] == 1)
    mv = [M[i]['mv'] for i in idx if M[i]['mv'] is not None]; mvn = sum(1 for x in mv if x > 1e-4)
    md = sorted(M[i]['mind'] for i in idx if M[i]['mind'] is not None)
    pm = sorted(M[i]['pmv'] for i in idx)
    fxs = [i for i in idx if M[i]['fx'] == 1]
    if fxs: name += ' [fx on %d, after-fix resid %.3f, >1 pass %.3f]' % (len(fxs), sum(1 for i in fxs if M[i]['f'] > 0) / len(fxs), sum(1 for i in fxs if M[i]['np'] > 1) / len(fxs))
    print('%-22s ticks %5d  pushed %.3f  resid %.3f  yclamp %.3f  bv!=pe %d/%d (max %.4g)  hit-dist p10/p50 %s  push-move p50/p90 %.4g/%.4g' % (
        name, n, pushed / n, res / n, yc / n, mvn, len(mv), max(mv) if mv else 0,
        ('%.4g/%.4g' % (md[len(md) // 10], md[len(md) // 2])) if md else '-', pm[n // 2], pm[(9 * n) // 10]))
tm = [t['m'] for t in ticks]
import bisect
def win(m): return list(range(bisect.bisect_left(tm, m - WIN * 24e6), bisect.bisect_right(tm, m)))
print('flight ticks %d  eye losses %d  other losses %d  f20 %s' % (len(ticks), len(eye), len(other), M[len(M) // 2]['f20']))
summ(range(len(ticks)), 'all ticks')
for s in (0, 1): summ([i for i in range(len(ticks)) if M[i]['fx'] == s], 'all ticks fx=%d' % s)
E = sorted(set(i for e in eye for i in win(e[0]))); O = sorted(set(i for e in other for i in win(e[0])))
summ(E, 'eye-loss windows'); summ(O, 'other-loss windows')
for sh in (-3.0, 3.0):
    summ(sorted(set(i for e in eye for i in win(e[0] + sh * 24e6))), 'eye windows %+gs ctl' % sh)
print('--- per eye loss: t, ref/drop minz, then per tick in window: dt_ms nh mind r yc mv pmv  | eye->target dist')
for m, t, rz, dz in eye:
    s = ' '.join('[%.0f %d %s %d %d %s %.3g]' % ((tm[i] - m) / 24e3, M[i]['nh'], '%.3g' % M[i]['mind'] if M[i]['mind'] is not None else '-', M[i]['r'], M[i]['yc'],
                                                 '%.2g' % M[i]['mv'] if M[i]['mv'] is not None else '-', M[i]['pmv']) for i in win(m))
    print('t=%7.2f ref %04X drop %04X %s' % (t, rz, dz, s))
