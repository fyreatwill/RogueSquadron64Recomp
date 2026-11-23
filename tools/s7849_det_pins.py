#!/usr/bin/env python3
"""s7849: derive the det-pair port pins from a retail oracle log (s7847 recipe, RS64_ORACLE_FPR=0,4,6,14,20 + watch-pc
0x800FA738/0x800FA7D0 + RS64_XTRACE_MEM ...800FA730:0:80003470:1).
Prints shell lines: SEED=<tick-0 rngSeed> DT_AT=<tick:HEX,...> NTICKS=<n> NDT=<n>.
SEED = m=80003470 value on the first pc=800fa730 [xtrace] row. DT_AT = every tick whose retail snapped dt != 3D088888,
except raw-dt-0 ticks (the dt-0 clamp, which the port reproduces natively). Exit 2 if no seed / no ticks / >512 dt pins
(apply_s7844_dt_at.py cap)."""
import re, sys
# s7858: the oracle's [vi-poll] printf (another thread) can splice into a [hit] line and push its tail (gprs + fpr:) onto the next
# line (r1 of s7857/v14: one 0x800FA738 hit at tick 886).  The old parser dropped that hit and indexed dt by LIST POSITION, so every
# pin after it landed one tick early (a fake port-side 1-2 ULP transient at t892-899).  Now: rejoin spliced lines, key each dt by the
# record-row ordinal (count of 800fa730 [xtrace] rows before the hit), and exit 2 if any tick lacks a dt or has two.
rx = re.compile(r'^\[hit\] x addr=\w+ pc=0x(\w+) .* n=(\d+) .*?fpr: f0=(\w+) f4=(\w+) f6=(\w+) f14=(\w+) f20=(\w+)')
splice = re.compile(r'\[vi-poll(?:-raw)?\] .*$')
def lines(path):
    held = None
    for ln in open(path, errors='replace'):
        ln = ln.rstrip('\n')
        if held is not None:
            if ln.startswith(' '): yield held + ln; held = None; continue
            yield held; held = None
        if ln.startswith('[hit] ') and '[vi-poll' in ln and 'fpr:' not in ln:
            held = splice.sub('', ln); continue
        yield ln
    if held is not None: yield held
seed = None; D = {}; cur = None; rows = 0; dup = []; spliced = 0
for ln in lines(sys.argv[1]):
    if ln.startswith('[xtrace] ') and 'pc=800fa730' in ln:
        if seed is None:
            m = re.search(r'm=80003470:([0-9a-f]{8})', ln); seed = m and m.group(1)
        rows += 1; continue
    m = rx.match(ln)
    if not m: continue
    pc, f20 = m.group(1), m.group(7)
    if pc == '800fa738': cur = (f20, rows - 1)
    elif pc == '800fa7d0' and cur is not None:
        if cur[1] in D: dup.append(cur[1])
        D[cur[1]] = (cur[0], f20); cur = None
n = (max(D) + 1) if D else 0
miss = [i for i in range(n) if i not in D]
T = [D.get(i, ('00000000', '3d088888')) for i in range(n)]
pins = [(i, fin) for i, (raw, fin) in enumerate(T) if fin != '3d088888' and raw != '00000000']
print('SEED=%s' % seed); print('DT_AT=%s' % ','.join('%d:%s' % (i, f.upper()) for i, f in pins))
print('NTICKS=%d' % n); print('NDT=%d' % len(pins))
if miss or dup: print('# s7858: ticks missing a dt %s, duplicated %s' % (miss[:8], dup[:8]), file=sys.stderr)
sys.exit(2 if (not seed or not T or len(pins) > 512 or miss or dup) else 0)
