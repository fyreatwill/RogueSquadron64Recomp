#!/usr/bin/env python3
"""s6816 G3 FPS60 enemy-bolt attribution over ROGUESQ_RAND_TRACE logs with the s6816 bolt rows (tools/fixup_rand_trace.py,
rs64_bolt_mark): tag b0170000 = per-tick bolt state within 40 units of the player, b0170005 = msg-5 hit send (victim id).
800fa730 tick rows carry the player object m=80137db0 (hp float word 51, pos words 4..6 = 0x80137DC0).
Per bolt instance (node address + monotonic age): closest approach to the player (linear interpolation of the relative
position between consecutive ticks), whether it hit the player, and the miss vector at closest approach split into the
component along the player's velocity (negative = the bolt passes BEHIND the player = trailing aim) and across it.
Player victim id = the victim id of hit sends that coincide with an hp drop (>5) in the same or next tick.
Usage: g3_bolt_attrib.py <dir> a30_s1 ... b60_s1 ...   (hz from the run name: a30* = 30, b60* = 60)"""
import sys, struct, collections, math
fl = lambda w: struct.unpack('>f', struct.pack('>I', w))[0]
D = sys.argv[1]; RUNS = sys.argv[2:]
hzof = lambda f: int(f[1:3])
vec = lambda s: [float(x) for x in s.split(',')]
sub = lambda a, b: [a[i] - b[i] for i in range(3)]
dot = lambda a, b: sum(a[i] * b[i] for i in range(3))
nrm = lambda a: math.sqrt(dot(a, a))

def load(f):
    ticks, rows = [], []          # ticks: [hp, plpos]; rows: (tick, kind, victim, dict)
    for ln in open('%s/%s.rand.txt' % (D, f)):
        x = ln.split()
        if len(x) < 4: continue
        if x[2] == '800fa730':
            m = [y for y in x[4:] if y.startswith('m=80137db0')]
            if m:
                w = [int(v, 16) for v in m[0].split(':')[1].split(',')]
                ticks.append((fl(w[51]), [fl(w[4]), fl(w[5]), fl(w[6])]))
            else:
                ticks.append((None, None))
            continue
        if x[2] in ('b0170000', 'b0170005') and ticks:
            d = dict(kv.split('=', 1) for kv in x[4:])
            rows.append((len(ticks) - 1, x[2] == 'b0170005', int(x[3], 16), d))
    return ticks, rows

def analyse(f):
    hz = hzof(f); ticks, rows = load(f)
    i0 = 16 * hz
    end = next((i for i in range(1, len(ticks)) if ticks[i][0] is not None and ticks[i][0] <= 0 < (ticks[i - 1][0] or 0)), len(ticks))
    drop = {i for i in range(1, len(ticks)) if ticks[i][0] is not None and ticks[i - 1][0] is not None and ticks[i - 1][0] - ticks[i][0] > 5}
    vic = collections.Counter(r[2] for r in rows if r[1] and (r[0] in drop or r[0] + 1 in drop))
    pid = vic.most_common(1)[0][0] if vic else None
    # bolt instances
    inst = {}; cur = {}
    for t, hit, v, d in rows:
        if not (i0 <= t < end): continue
        node = d['bolt']; age = float(d['age'])
        k = cur.get(node)
        if k is None or age + 1e-6 < inst[k]['last_age']:
            k = (node, t); cur[node] = k
            inst[k] = {'rows': [], 'hit': False, 'own': d['own'], 'dmg': int(d['dmg']), 'last_age': age}
        b = inst[k]; b['last_age'] = age
        if hit:
            if v == pid: b['hit'] = True; b['hit_t'] = t
            b.setdefault('victims', set()).add(v)
        else:
            b['rows'].append((t, vec(d['p']), vec(d['v']), vec(d['pl'])))
    out = []
    for k, b in inst.items():
        R = b['rows']
        if not R: continue
        best = (1e9, None, None)
        for j in range(len(R)):
            t, p, v, q = R[j]
            r0 = sub(p, q)
            cand = [(nrm(r0), r0, j)]
            if j + 1 < len(R) and R[j + 1][0] == t + 1:
                r1 = sub(R[j + 1][1], R[j + 1][3]); dr = sub(r1, r0); dd = dot(dr, dr)
                if dd > 0:
                    u = max(0.0, min(1.0, -dot(r0, dr) / dd)); rr = [r0[i] + u * dr[i] for i in range(3)]
                    cand.append((nrm(rr), rr, j))
            for c in cand:
                if c[0] < best[0]: best = c
        dmin, rmin, j = best
        t = R[j][0]
        # player velocity from tick positions (units / s)
        q0 = ticks[t - 1][1] if t >= 1 and ticks[t - 1][1] else None; q1 = ticks[t][1]
        vp = [(q1[i] - q0[i]) * hz for i in range(3)] if q0 and q1 else [0, 0, 0]
        sp = nrm(vp); along = dot(rmin, vp) / sp if sp > 1e-6 else 0.0
        across = math.sqrt(max(0.0, dmin * dmin - along * along))
        out.append({'dmin': dmin, 'hit': b['hit'], 'along': along, 'across': across, 'vp': sp, 'vb': nrm(R[j][2]),
                    'own': b['own'], 'dmg': b['dmg'], 'n': len(R)})
    T = (end - i0) / hz
    return hz, pid, T, out, len(drop & set(range(i0, end))), sum(1 for r in rows if r[1] and r[2] == pid and i0 <= r[0] < end)

BINS = [0, 1, 2, 3, 4, 6, 10, 20, 40]
agg = collections.defaultdict(list)
for f in RUNS:
    hz, pid, T, out, nd, nh = analyse(f)
    hits = [o for o in out if o['hit']]
    print('%-7s pid=%s alive %.0f s  bolts<40u %d (%.2f/s)  player-hit bolts %d  hit sends %d  hp drops %d  dmin(hit) max %.2f'
          % (f, '%04x' % pid if pid is not None else '-', T, len(out), len(out) / T, len(hits), nh, nd,
             max([o['dmin'] for o in hits] or [0])))
    agg[hz] += [dict(o, T=T) for o in out]
    agg[('T', hz)].append(T)
for hz in (30, 60):
    O = agg[hz]; T = sum(agg[('T', hz)])
    if not O: continue
    print('\n== %d Hz arm: %d bolt passes within 40u over %.0f alive s (%.2f/s)' % (hz, len(O), T, len(O) / T))
    for lo, hi in zip(BINS, BINS[1:]):
        S = [o for o in O if lo <= o['dmin'] < hi]
        h = sum(o['hit'] for o in S)
        al = sorted(o['along'] for o in S if not o['hit'])
        med = al[len(al) // 2] if al else float('nan')
        print('  dmin %4.1f-%4.1f  passes %5d (%.3f/s)  hits %3d (%5.1f%%)  miss along-vplayer median %+6.2f  frac behind %.2f'
              % (lo, hi, len(S), len(S) / T, h, 100.0 * h / len(S) if S else 0, med,
                 sum(a < 0 for a in al) / len(al) if al else float('nan')))
    vb = sorted(o['vb'] for o in O); vp = sorted(o['vp'] for o in O)
    print('  bolt speed median %.1f u/s, player speed median %.1f u/s' % (vb[len(vb) // 2], vp[len(vp) // 2]))

# hp writer census (s6816 hpwatch rows b017dd00: writer fn + host backtrace), per alive game second from 16 s
print('\n== hp drop sources (rows b017dd00), per alive game second from 16 s')
src = collections.defaultdict(lambda: collections.defaultdict(float))
for f in RUNS:
    hz = hzof(f); k = -1; c = collections.Counter(); T = None
    ticks, _ = load(f)
    end = next((i for i in range(1, len(ticks)) if ticks[i][0] is not None and ticks[i][0] <= 0 < (ticks[i - 1][0] or 0)), len(ticks))
    for ln in open('%s/%s.rand.txt' % (D, f)):
        x = ln.split()
        if len(x) < 4: continue
        if x[2] == '800fa730': k += 1; continue
        if x[2] != 'b017dd00' or not (16 * hz <= k < end): continue
        d = dict(kv.split('=', 1) for kv in x[4:])
        a, b = (float(v) for v in d['hp'].split(','))
        chain = d['bt'].split('<')
        j = chain.index('slotDispatcherIter') if 'slotDispatcherIter' in chain else -1
        via = chain[j + 1] if 0 <= j < len(chain) - 1 else '?'   # sender = frame above the first message dispatch
        c['%s/%s/%d' % (d['fn'], via, round(a - b))] += 1
    T = (end - 16 * hz) / hz
    print('%-7s alive %.0f s  ' % (f, T) + '  '.join('%s=%.3f/s' % (kk, v / T) for kk, v in sorted(c.items())))
