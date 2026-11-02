#!/usr/bin/env python3
"""s6791 G3f: rebuild the retail craft-select camera (0x800CD670 +0x2C..+0x5C) from a tools/g3f_retail_pan.sh oracle log
and print per-pan timelines in the tools/g3f_pan_cmp.py format. The camera stores are swc1, which the oracle's
store-field-dump cannot decode (scalar_mask 0, source_value = a GPR), so each word's value history is read from
pre_store_word (one frame late, uniformly). Time axis = snapshots / 30 (retail ~30 game fps; approximate).
usage: g3f_retail_cam.py oracle.log"""
import sys, math, struct, re
mem, snaps, cnt = {}, [], {}
f2 = lambda v: struct.unpack('>f', struct.pack('>I', v))[0]
rx = re.compile(r'origin=(\S+) .*store_addr=0x(\w+) .*pre_store_word=0x(\w+)')
for ln in open(sys.argv[1]):
    if not ln.startswith('[store-field-dump]'): continue
    o, a, pv = rx.search(ln).groups(); a = int(a, 16) & ~3; mem[a] = int(pv, 16); cnt[a] = cnt.get(a, 0) + 1
    if a == 0x0CD6C8 and all((0x0CD69C + 4 * k) in mem for k in range(12)):
        snaps.append([f2(mem[0x0CD69C + 4 * k]) for k in range(12)])
print('stores per word', {hex(k): v for k, v in sorted(cnt.items())}, 'snaps', len(snaps))
pos = [s[9:12] for s in snaps]; yaw = [math.degrees(math.atan2(s[2], s[0])) for s in snaps]
segs = []
for i in (i for i in range(1, len(pos)) if math.dist(pos[i], pos[i - 1]) > 0.02):
    if not segs or i - segs[-1][1] > 30: segs.append([i, i])
    else: segs[-1][1] = i
for s, e in segs:
    a, b = max(0, s - 1), min(len(pos) - 1, e + 150); p0, pf = pos[a], pos[b]; D = math.dist(p0, pf)
    y0, yf = yaw[a], yaw[b]; dy = (yf - y0 + 540) % 360 - 180
    if D < 1: continue
    tf = lambda f: next((i - a) / 30 for i in range(a, b + 1) if math.dist(pos[i], p0) >= f * D)
    ty = lambda f: next(((i - a) / 30 for i in range(a, b + 1) if abs((yaw[i] - y0 + 540) % 360 - 180) >= f * abs(dy)), -1)
    over = max(math.dist(pos[i], p0) for i in range(a, b + 1)) - D
    print('seg %d-%d dist %.1f yaw %.1f->%.1f over %.2f | ' % (s, e, D, y0, yf, over) + ' '.join('p%d=%.2f' % (f * 100, tf(f)) for f in (.1, .5, .9, .99)) + ' | ' + ' '.join('y%d=%.2f' % (f * 100, ty(f)) for f in (.1, .5, .9, .99)))
