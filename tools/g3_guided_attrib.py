#!/usr/bin/env python3
"""s6816 G3 FPS60 guided-projectile attribution (lvl14: the 50-hp player hits all come from guidedEffectNpcHandler,
s6816 hpwatch). Reads ROGUESQ_RAND_TRACE logs with the s6816b rows (tools/fixup_rand_trace.py, rs64_guided_mark):
b0170010 = every guided missile every tick at its swept hit test, b0170011 = the test returned a victim.
800fa730 tick rows carry the player object (hp word 51). Player id = victim id of b0170011 rows coinciding with an
hp drop (> 5) in the same or next tick.
Per missile instance (data pointer + monotonic age): spawn tick, owner, target id, lock flag, lifetime (game s),
closest approach to the player, outcome (hit player / hit other / expired). Per arm, per alive game second from 16 s:
missiles launched, launched AT the player (target == player id), their hit fraction, and closest-approach bins.
Usage: g3_guided_attrib.py <dir> a30_s1 ... b60_s1 ...   (hz from the run name: a30* = 30, b60* = 60)"""
import sys, struct, collections, math
fl = lambda w: struct.unpack('>f', struct.pack('>I', w))[0]
D = sys.argv[1]; RUNS = sys.argv[2:]
hzof = lambda f: int(f[1:3])
vec = lambda s: [float(x) for x in s.split(',')]
dist = lambda a, b: math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))

def load(f):
    hp, rows = [], []
    for ln in open('%s/%s.rand.txt' % (D, f)):
        x = ln.split()
        if len(x) < 4: continue
        if x[2] == '800fa730':
            m = [y for y in x[4:] if y.startswith('m=80137db0')]
            hp.append(fl(int(m[0].split(':')[1].split(',')[51], 16)) if m else None); continue
        if x[2] in ('b0170010', 'b0170011') and hp:
            if x[2] == 'b0170011' and x[3] == 'ffff': continue   # the post-test mark fires every tick; keep real victims
            rows.append((len(hp) - 1, x[2] == 'b0170011', int(x[3], 16), dict(kv.split('=', 1) for kv in x[4:])))
    return hp, rows

agg = collections.defaultdict(list)
for f in RUNS:
    hz = hzof(f); hp, rows = load(f); i0 = 16 * hz
    end = next((i for i in range(1, len(hp)) if hp[i] is not None and hp[i] <= 0 < (hp[i - 1] or 0)), len(hp))
    drop = {i for i in range(1, len(hp)) if hp[i] is not None and hp[i - 1] is not None and hp[i - 1] - hp[i] > 5}
    vic = collections.Counter(r[2] for r in rows if r[1] and (r[0] in drop or r[0] + 1 in drop))
    pid = vic.most_common(1)[0][0] if vic else None
    inst, cur = {}, {}
    for t, hit, v, d in rows:
        gm = d['gm']; age = float(d['age'])
        k = cur.get(gm)
        if not hit and (k is None or age + 1e-6 < inst[k]['age']):
            k = (gm, t); cur[gm] = k
            inst[k] = {'t0': t, 'own': d['own'], 'tgt': [], 'lk': set(), 'dmin': 1e9, 'out': 'expired', 'age': age, 'dmg': d['dmg']}
        if k is None: continue
        b = inst[k]
        if hit:
            b['out'] = 'player' if v == pid else 'other'; continue
        b['age'] = age; b['t1'] = t
        b['tgt'].append(int(d['tgt'], 16)); b['lk'].add(d['lk'])
        b['dmin'] = min(b['dmin'], dist(vec(d['p']), vec(d['pl'])))
    M = [b for b in inst.values() if i0 <= b['t0'] < end]
    T = (end - i0) / hz
    atp = [b for b in M if pid is not None and pid in b['tgt']]
    print('%-7s pid=%s alive %.0f s  missiles %d (%.3f/s)  aimed at player %d (%.3f/s)  hit player %d (%.3f/s)  '
          'hit-frac(aimed) %.2f  life med %.2f s  hp drops %d'
          % (f, '%04x' % pid if pid is not None else '-', T, len(M), len(M) / T, len(atp), len(atp) / T,
             sum(b['out'] == 'player' for b in M), sum(b['out'] == 'player' for b in M) / T,
             sum(b['out'] == 'player' for b in atp) / len(atp) if atp else float('nan'),
             sorted(b['age'] for b in M)[len(M) // 2] if M else float('nan'), len(drop & set(range(i0, end)))))
    own = collections.Counter(b['own'] for b in atp)
    print('         owners of player-aimed missiles: ' + ' '.join('%s:%d' % kv for kv in own.most_common(8)))
    agg[hz] += atp; agg[('T', hz)].append(T)
for hz in (30, 60):
    A = agg[hz]; T = sum(agg[('T', hz)])
    if not A: continue
    print('\n== %d Hz: %d player-aimed missiles over %.0f alive s (%.3f/s)' % (hz, len(A), T, len(A) / T))
    for lo, hi in ((0, 1), (1, 2), (2, 4), (4, 8), (8, 16), (16, 1e9)):
        S = [b for b in A if lo <= b['dmin'] < hi]
        print('  dmin %4.0f-%-4.0f n %4d  hit player %4d  expired %4d  hit other %3d  life med %.2f s'
              % (lo, min(hi, 999), len(S), sum(b['out'] == 'player' for b in S), sum(b['out'] == 'expired' for b in S),
                 sum(b['out'] == 'other' for b in S), sorted(b['age'] for b in S)[len(S) // 2] if S else float('nan')))
