#!/usr/bin/env python3
"""s6817: lvl14 terrain-scrape contact census from a port rand/xtrace trace (800fa730 rows with m=80137db0, dt pinned).
Per run: contact ticks in [T0,T1] (hp drop of 15-25 in one tick = 20-hp collision hit; 50-hp missiles excluded), the craft
angle words +0xD8/+0xDC/+0xE0 (deg) and world dpos/dt at T1, and position at TPOS. usage: g3_scrape_contacts.py HZ TRACE..
env T0 (15.0) T1 (16.5) TPOS (40)."""
import os, struct, sys
f32 = lambda h: struct.unpack('>f', bytes.fromhex(h))[0]
hz = float(sys.argv[1]); t0 = float(os.environ.get('T0', 15.0)); t1 = float(os.environ.get('T1', 16.5))
tpos = float(os.environ.get('TPOS', 40))
for p in sys.argv[2:]:
    n = 0; prev = None; contacts = []; at1 = atp = None
    for ln in open(p):
        x = ln.split()
        if len(x) < 5 or x[2] != '800fa730': continue
        w = [q for q in x if q.startswith('m=80137db0')]
        if not w: continue
        w = w[0].split(':')[1].split(','); t = n / hz; n += 1
        pos = [f32(w[i]) for i in (4, 5, 6)]; ang = [f32(w[i]) for i in (54, 55, 56)]; hp = f32(w[51])
        if prev and t0 <= t <= t1 and 15 <= prev[1] - hp <= 25:
            contacts.append((round(t, 3), [round(ang[i] - prev[2][i], 2) for i in range(3)]))
        if prev and at1 is None and t >= t1:
            at1 = (ang, [(pos[i] - prev[0][i]) * hz for i in range(3)])
        if atp is None and t >= tpos: atp = pos
        prev = (pos, hp, ang)
    print(f"{os.path.basename(p)}: {len(contacts)} contacts {[c[0] for c in contacts]}")
    print("   dang/contact", [c[1] for c in contacts])
    if at1: print(f"   at {t1}s ang {[round(a, 2) for a in at1[0]]} vel {[round(v, 2) for v in at1[1]]}")
    if atp: print(f"   pos@{tpos}s {[round(v, 2) for v in atp]}")
