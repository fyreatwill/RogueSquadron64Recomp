#!/usr/bin/env python3
"""s6873 G3: where do two no-input runs fork? Reads the rand.txt of tools/g3_optin_pose_arms.sh arms (800FA730 tick row dumps dt at
sp+0x30, player pos 0x80137DC0, hp 0x80137E7C; pin=OLD = the real dt under a pin). Prints per arm the dt spread, then per pair
the first tick whose pos, rand stream or hp differs. Rand rows = every row that is not a tick, pointer or bolt row.
Usage: g3_fork_trace.py ARMS_DIR BASE ARM [ARM ...]   (step=2 in an arm name compares its tick 2n to the base tick n)"""
import os, struct, sys
SKIP = ('8008ee84', '8006bec8', '8006c010', '8006c018', '8006c0fc', 'b0170000')

def f(w):
    return struct.unpack('>f', bytes.fromhex(w))[0]

def load(root, arm):
    t, rows, hits = [], [], []
    for l in open(os.path.join(root, arm, 'rand.txt'), errors='replace'):
        p = l.split()
        if len(p) < 4:
            continue
        if p[2] == 'b0170005':
            hits.append((len(t), l.strip()[:90]))
        elif p[2] == '800fa730':
            m = [x.split(':')[1].split(',') for x in p[4:] if x.startswith('m=')]
            pin = [x[4:] for x in p[4:] if x.startswith('pin=')]
            if len(m) < 3:
                continue
            t.append(dict(vi=int(p[1]), dt=m[0][0], raw=pin[0] if pin else m[0][0], pos=tuple(m[1]), hp=m[2][0], r=len(rows)))
        elif p[2] not in SKIP:
            rows.append((p[2], p[3]))
    return t, rows, hits

def main():
    root, base, arms = sys.argv[1], sys.argv[2], sys.argv[3:]
    D = {a: load(root, a) for a in [base] + arms}
    for a, (t, r, h) in D.items():
        d = sorted(f(x['raw']) for x in t[1:]) or [0]
        print('%-6s ticks %5d rand %6d hits %3d  real dt min %.5f med %.5f max %.5f  ticks with dt != median %d' % (
            a, len(t), len(r), len(h), d[0], d[len(d) // 2], d[-1], sum(1 for x in d if x != d[len(d) // 2])))
    bt, br, _ = D[base]
    for a in arms:
        t, r, h = D[a]
        n = min(len(bt), len(t))
        fp = next((i for i in range(n) if t[i]['pos'] != bt[i]['pos']), None)
        fh = next((i for i in range(n) if t[i]['hp'] != bt[i]['hp']), None)
        fr = next((i for i in range(min(len(br), len(r))) if r[i] != br[i]), None)
        ft = next((i for i in range(n) if bt[i]['r'] > (fr if fr is not None else 1 << 60)), None)
        print('%s vs %s: first pos diff tick %s, hp diff tick %s, rand diff row %s (tick %s) of %d common ticks' % (a, base, fp, fh, fr, ft, n))
        if fp is not None:
            for i in range(max(0, fp - 1), min(n, fp + 2)):
                q = lambda x: ','.join('%.4f' % f(w) for w in x[i]['pos']) + ' dt %.5f hp %s' % (f(x[i]['raw']), x[i]['hp'])
                print('   t%d %s | %s' % (i, q(bt), q(t)))
        big = next((i for i in range(n) if max(abs(f(u) - f(v)) for u, v in zip(t[i]['pos'], bt[i]['pos'])) > 0.5), None)
        print('   first |dpos| > 0.5 at tick %s' % big)
        if big is not None:
            print('   hits near: ' + ' ; '.join(x[1][:60] for x in (D[base][2] + h) if abs(x[0] - big) < 30)[:400])

main()
