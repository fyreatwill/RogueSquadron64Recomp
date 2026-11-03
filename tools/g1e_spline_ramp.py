#!/usr/bin/env python3
"""s6830 G1e FPS60: updateSplineCraftTransform per-tick quanta check from ROGUESQ_TICK_TRACE files.
Per arm: speed +0x140 (trace pc 0x800B0ED4, value before the step) and scale +0xE8 (pc 0x800B0BA8, before the *=1.01):
per consecutive-tick pair, change per GAME second (d / tick dt) while ramping (speed |v| < 180).
Expected: a30 60 u/s^2 (2.0 per 1/30 s tick); FPS60 fix 60; FPS60 FQUANTA=0 120 (2.0 per 1/60 s tick).
Scale: log growth per game s = 30*ln(1.01) = 0.299 (a30, fix), 0.597 unfixed.
Usage: g1e_spline_ramp.py arm.tick.bin [...]"""
import sys, struct, math, collections
from statistics import median
for path in sys.argv[1:]:
    d = open(path, 'rb').read(); dt = {}; r = collections.defaultdict(list)
    for pc, a, v, tk in struct.iter_unpack('<4I', d[:len(d) // 16 * 16]):
        if pc == 0: dt[tk] = struct.unpack('<f', struct.pack('<I', v))[0]
        elif pc in (0x800B0ED4, 0x800B0BA8): r[pc].append((tk, a, struct.unpack('<f', struct.pack('<I', v))[0]))
    out = []
    for pc, name in ((0x800B0ED4, 'speed'), (0x800B0BA8, 'scale')):
        last = {}; rates = []
        for tk, a, x in r[pc]:
            if a in last and last[a][0] == tk - 1 and 0 < dt.get(tk - 1, 0) < 0.2:
                p = last[a][1]
                if name == 'speed' and p != x and abs(x) < 180: rates.append(abs(x - p) / dt[tk - 1])
                if name == 'scale' and p > 0 and x > 0 and p != x: rates.append(math.log(x / p) / dt[tk - 1])
            last[a] = (tk, x)
        out.append('%s n=%d med/gs=%s' % (name, len(rates), ('%.3f' % median(rates)) if rates else '-'))
    print(path, ' | '.join(out))
