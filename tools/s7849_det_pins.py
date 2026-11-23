#!/usr/bin/env python3
"""s7849: derive the det-pair port pins from a retail oracle log (s7847 recipe, RS64_ORACLE_FPR=0,4,6,14,20 + watch-pc
0x800FA738/0x800FA7D0 + RS64_XTRACE_MEM ...800FA730:0:80003470:1).
Prints shell lines: SEED=<tick-0 rngSeed> DT_AT=<tick:HEX,...> NTICKS=<n> NDT=<n>.
SEED = m=80003470 value on the first pc=800fa730 [xtrace] row. DT_AT = every tick whose retail snapped dt != 3D088888,
except raw-dt-0 ticks (the dt-0 clamp, which the port reproduces natively). Exit 2 if no seed / no ticks / >32 dt pins
(apply_s7844_dt_at.py cap)."""
import re, sys
rx = re.compile(r'^\[hit\] x addr=\w+ pc=0x(\w+) .* n=(\d+) .*?fpr: f0=(\w+) f4=(\w+) f6=(\w+) f14=(\w+) f20=(\w+)')
seed = None; T = []; cur = None
for ln in open(sys.argv[1], errors='replace'):
    if seed is None and ln.startswith('[xtrace] ') and 'pc=800fa730' in ln:
        m = re.search(r'm=80003470:([0-9a-f]{8})', ln); seed = m and m.group(1)
    m = rx.match(ln)
    if not m: continue
    pc, f20 = m.group(1), m.group(7)
    if pc == '800fa738': cur = f20
    elif pc == '800fa7d0' and cur is not None: T.append((cur, f20)); cur = None
pins = [(i, fin) for i, (raw, fin) in enumerate(T) if fin != '3d088888' and raw != '00000000']
print('SEED=%s' % seed); print('DT_AT=%s' % ','.join('%d:%s' % (i, f.upper()) for i, f in pins))
print('NTICKS=%d' % len(T)); print('NDT=%d' % len(pins))
sys.exit(2 if (not seed or not T or len(pins) > 32) else 0)
