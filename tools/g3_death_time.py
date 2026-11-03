#!/usr/bin/env python3
"""s6814: per-run passive-player death time from a port rand/xtrace trace whose 800fa730 rows carry
m=80137db0 (player object, hp float at +0xCC) and m=8010c9e0 (mission flags; +0x3C = 0x8010CA1C).
Game time = 800fa730 row ordinal / HZ (dt pinned). usage: g3_death_time.py HZ TRACE..."""
import struct, sys
fl = lambda w: struct.unpack('>f', struct.pack('>I', w))[0]
hz = float(sys.argv[1])
for p in sys.argv[2:]:
    k = 0; prev = None; hits = 0; h50 = 0; dmg = 0.0; death = flag = None; hp0 = None; first_div = None
    for ln in open(p):
        f = ln.split()
        if len(f) < 5 or f[2] != '800fa730': continue
        m = {x[2:].split(':')[0]: x[2:].split(':')[1].split(',') for x in f[4:] if x.startswith('m=')}
        hp = fl(int(m['80137db0'][0xCC // 4], 16)); fw = int(m['8010c9e0'][15], 16)
        if hp0 is None: hp0 = hp
        if prev is not None and hp < prev - 0.5 and death is None:
            hits += 1; dmg += prev - hp
            if k / hz > 16 and abs(prev - hp - 50) < 1 and hp > 0: h50 += 1  # 50-hp hits after the shared 15.4-15.9 s burst
        if death is None and prev is not None and prev > 0 and hp <= 0: death = k / hz
        if flag is None and fw & 0x100: flag = k / hz
        prev = hp; k += 1
    t = death if death is not None else k / hz
    print('%-34s ticks=%5d death=%s flag0x100=%s hits=%d dmg=%.0f dmg/s=%.2f hit50/s(t>16)=%.3f' % (p.split('/')[-1], k,
          'none' if death is None else '%.2f' % death, 'none' if flag is None else '%.2f' % flag, hits, dmg, dmg / t, h50 / (t - 16)))
