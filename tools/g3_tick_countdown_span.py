#!/usr/bin/env python3
"""s6822 G3 FPS60: gap-tolerant countdown spans from ROGUESQ_TICK_TRACE dumps. g3_tick_timer_durations.py ends a run on a
>4-tick gap, which shreds sites that execute intermittently (once per ~1 game s); here a run per (site, field) lasts
until the value steps UP (countdown restart), and its span = game time from the first to the last execution in it.
Also prints executions per game second: a per-tick site doubles at FPS60, an event-gated one does not.
Usage: g3_tick_countdown_span.py --sites=800DAB64,... ARM.tick.bin [...]"""
import struct, sys, statistics as st, collections
args = [a for a in sys.argv[1:] if not a.startswith('--')]
sites = [int(x, 16) for x in next(a for a in sys.argv if a.startswith('--sites=')).split('=', 1)[1].split(',')]
for p in args:
    b = open(p, 'rb').read(); b = b[:len(b) // 16 * 16]
    t, ev = {}, collections.defaultdict(list)
    for pc, a, v, k in struct.iter_unpack('<IIII', b):
        if pc == 0: t[k] = struct.unpack('<f', struct.pack('<I', a))[0]
        elif pc in sites: ev[(pc, a)].append((k, v - (1 << 32) if v & 0x80000000 else v))
    gs = (max(t.values()) - min(t.values())) if t else 0
    print(f'# {p}: {len(t)} ticks, {gs:.1f} game s')
    for pc in sites:
        spans, n = [], 0
        for (q, a), e in ev.items():
            if q != pc: continue
            n += len(e); s0 = e[0]
            for prev, cur in zip(e, e[1:] + [None]):
                if cur is None or cur[1] > prev[1]:
                    if prev[0] in t and s0[0] in t and prev is not s0: spans.append(t[prev[0]] - t[s0[0]])
                    s0 = cur
        print(f'  {pc:08X} ex/gs {n / gs if gs else 0:6.2f}  runs {len(spans):4d}  median span {st.median(spans) if spans else 0:.3f} s'
              f'  mean {st.mean(spans) if spans else 0:.3f}')
