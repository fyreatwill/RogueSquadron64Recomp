#!/usr/bin/env python3
"""s7101 fps60-wall-camera: per-tick flight camera position from the ROGUESQ_S7101_CAMW store log.

Per game tick (fc = frame counter 0x8011A890 at the store) take the camera translation the chase code wrote
(updatePlayerVehicleByControlMode stores to cam+0x4C/0x50/0x54) and the branch it took:
  snap   0x8004D7F4.. (distance <= 0.01: pos = target)
  chase  0x8004D7E0.. (pos += speed*dt*unit(target-pos))
  blend  0x8004D680.. (the cam+0xA4 timer branch)
  fixed  0x8004D4BC.. (mode with no chase: pos = matrix x offset)
World reversal = negative dot product of consecutive per-tick position steps.
With soak result + drops csv: the same statistic in the s7100 episode windows (-PRE..+POST s around each episode).
usage: s7101_camw.py camw.txt [drops.csv soak_res.log] [--pre 0.3] [--post 0.1]"""
import sys, re, bisect, ast
a = sys.argv[1:]; PRE, POST = 0.3, 0.1
def opt(name):
    global a
    if name in a:
        i = a.index(name); v = float(a[i + 1]); del a[i:i + 2]; return v
PRE = opt('--pre') or PRE; POST = opt('--post') or POST
BR = {0x8004D7E0: 'chase', 0x8004D7E4: 'chase', 0x8004D7EC: 'chase', 0x8004D680: 'blend', 0x8004D684: 'blend', 0x8004D688: 'blend',
      0x8004D4BC: 'fixed', 0x8004D4C4: 'fixed', 0x8004D4D0: 'fixed'}
rx = re.compile(r'^st m=(\d+) lim=(\d+) fc=(\d+) pc=([0-9A-F]+) ra=\S+ fn=updatePlayerVehicleByControlMode off=(\w+) w=\S+ v=(\S+)')
ticks = {}  # fc -> dict
order = []
for l in open(a[0], errors='replace'):
    g = rx.match(l)
    if not g: continue
    fc = int(g.group(3)); pc = int(g.group(4), 16); off = int(g.group(5), 16)
    t = ticks.get(fc)
    if t is None:
        t = ticks[fc] = {'m': int(g.group(1)), 'lim': int(g.group(2)), 'p': [None] * 3, 'br': set()}; order.append(fc)
    if off in (0x4C, 0x50, 0x54): t['p'][(off - 0x4C) // 4] = float(g.group(6))
    t['br'].add(BR.get(pc, 'snap' if pc >= 0x8004D7F0 and pc < 0x8004D820 else 'other:%08X' % pc))
T = [ticks[f] for f in order if None not in ticks[f]['p']]
M = [t['m'] for t in T]
def rev(i):
    if i < 2: return False
    s1 = [T[i - 1]['p'][k] - T[i - 2]['p'][k] for k in range(3)]; s2 = [T[i]['p'][k] - T[i - 1]['p'][k] for k in range(3)]
    return sum(x * y for x, y in zip(s1, s2)) < 0
R = [rev(i) for i in range(len(T))]
hist = {}
for i, t in enumerate(T):
    k = (t['lim'], '+'.join(sorted(t['br']))); h = hist.setdefault(k, [0, 0]); h[0] += 1; h[1] += R[i]
for k in sorted(hist): print('TICKS lim=%d branch=%s n=%d world_rev=%d (%.4f)' % (k[0], k[1], hist[k][0], hist[k][1], hist[k][1] / max(1, hist[k][0])))
if len(a) >= 3:
    rows = [l.split(',') for l in open(a[1])][1:]
    cap0 = int(rows[0][6]) - float(rows[0][1]) * 24e6
    for l in open(a[2], errors='replace'):
        g = re.match(r'lim=(\d+) span .* times (\[.*\])', l)
        if not g: continue
        ts = ast.literal_eval(g.group(2)); ep = [t for i, t in enumerate(ts) if i == 0 or t - ts[i - 1] > 1.0]
        for t in ep:
            m = cap0 + t * 24e6; i0 = bisect.bisect_left(M, m - PRE * 24e6); i1 = bisect.bisect_right(M, m + POST * 24e6)
            br = {}
            for i in range(i0, i1):
                for b in T[i]['br']: br[b] = br.get(b, 0) + 1
            print('EP lim=%s t=%.1f ticks %d world_rev %d branches %s' % (g.group(1), t, i1 - i0, sum(R[i0:i1]), br))
            for i in range(i0, i1):
                st = [T[i]['p'][k] - T[i - 1]['p'][k] for k in range(3)] if i else [0, 0, 0]
                print('   fc=%d lim=%d %s pos=%.3f,%.3f,%.3f step=%.4f,%.4f,%.4f rev=%d' % (order[0] if False else 0, T[i]['lim'], '+'.join(sorted(T[i]['br'])), *T[i]['p'], *st, R[i]))
