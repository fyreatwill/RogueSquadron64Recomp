#!/usr/bin/env python3
"""s6873 G3: per-tick contact events from the rand.txt of tools/g3_optin_pose_arms.sh arms that dump the player object (XMEM
800FA730:0:80137DB0:64). A contact pass turns the craft 6 deg in one tick, so a jump of +0xDC (pitch, deg) by >= 3 in one tick is a
contact and jump/6 its pass count. The first dive after x > XMIN (default 90) is printed with its position.
Usage: g3_contact_pitch.py ARMS_DIR ARM [ARM ...]"""
import os, struct, sys
f = lambda w: struct.unpack('>f', bytes.fromhex(w))[0]
XMIN = float(os.environ.get('XMIN', 90))

def main():
    root = sys.argv[1]
    for a in sys.argv[2:]:
        T = 0.0; prev = None; ev = []
        for l in open(os.path.join(root, a, 'rand.txt'), errors='replace'):
            p = l.split()
            if len(p) < 6 or p[2] != '800fa730':
                continue
            d = {x.split(':')[0][2:]: x.split(':')[1].split(',') for x in p[4:] if x.startswith('m=')}
            if '80137db0' not in d:
                continue
            T += f(d['80165ef0'][0]); w = d['80137db0']; v = f(w[0xDC // 4])
            if prev is not None and abs(v - prev) >= 3:
                ev.append((T, f(w[4]), f(w[5]), f(w[6]), prev, v))
            prev = v
        print('%-5s dt %.5f contacts %d: %s' % (a, f(d['80165ef0'][0]), len(ev), ' '.join('t%.2f x%.1f %+.0f' % (e[0], e[1], e[5] - e[4]) for e in ev[:8])))

main()
