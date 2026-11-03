#!/usr/bin/env python3
"""s6821 G3 FPS60: offline analysis of ROGUESQ_TICK_TRACE dumps (tools/fixup_fps60_ticks.py). Per counter site:
executions per game second (a per-tick site doubles at FPS60 against 30 Hz), and per (site, field address) monotone
runs - countdown: values non-increasing, count-up: non-decreasing, a run ends on a reverse step or a >4-tick gap -
with each run's duration in GAME seconds (sum of tick dt over the ticks it spans). A frame-locked timer's median run
halves at FPS60; a fixed one matches 30 Hz.
Usage: g3_tick_timer_durations.py ARM.tick.bin [ARM2.tick.bin ...] [--sites 800C96B8,...] [--min-runs 3]"""
import struct, sys, statistics as st, collections
args = [a for a in sys.argv[1:] if not a.startswith('--')]
opt = {a.split('=')[0]: a.split('=', 1)[1] if '=' in a else '' for a in sys.argv[1:] if a.startswith('--')}
only = {int(x, 16) for x in opt['--sites'].split(',')} if opt.get('--sites') else None
min_runs = int(opt.get('--min-runs', 3))
try:
    sys.path.insert(0, __file__.rsplit('/', 1)[0])
    from g3_tick_counter_audit import scan
    names = {r[1]: (r[0], r[4], r[5]) for r in scan('../N64Recomp/RecompiledFuncs')}
except Exception:
    names = {}
def load(p):
    b = open(p, 'rb').read(); b = b[:len(b) // 16 * 16]
    tick_t, tick_dt, ev = {}, {}, collections.defaultdict(list)
    for pc, a, v, k in struct.iter_unpack('<IIII', b):
        if pc == 0:
            tick_t[k] = struct.unpack('<f', struct.pack('<I', a))[0]; tick_dt[k] = struct.unpack('<f', struct.pack('<I', v))[0]
        else:
            ev[pc].append((k, a, v - (1 << 32) if v & 0x80000000 else v))
    return tick_t, tick_dt, ev
res = {}
for p in args:
    tt, td, ev = load(p)
    ks = sorted(tt); gs = sum(td[k] for k in ks if td[k] > 0)
    out = {}
    for pc, L in ev.items():
        if only and pc not in only: continue
        step = names.get(pc, ('?', 0, ''))[1]
        per = collections.defaultdict(list)
        for k, a, v in L: per[a].append((k, v))
        runs = []
        for a, s in per.items():
            cur = [s[0]]
            for x in s[1:]:
                rev = (x[1] > cur[-1][1]) if step < 0 else (x[1] < cur[-1][1])
                if rev or x[0] - cur[-1][0] > 4:
                    runs.append(cur); cur = [x]
                else: cur.append(x)
            runs.append(cur)
        durs = [sum(td.get(k, 0) for k in range(r[0][0], r[-1][0] + 1)) for r in runs if len(r) > 1]
        out[pc] = (len(L), len(L) / gs if gs else 0, len(per), durs, [r[0][1] for r in runs if len(r) > 1])
    res[p] = (gs, len(ks), out)
    print('# %s: %d ticks, %.1f game s, %d sites seen' % (p, len(ks), gs, len(out)))
pcs = sorted({pc for r in res.values() for pc in r[2]})
print('%-10s %-40s %4s | ' % ('pc', 'func', 'step') + ' | '.join('%-30s' % p.rsplit('/', 1)[-1][:30] for p in args))
print('%-10s %-40s %4s | ' % ('', '', '') + ' | '.join('%-30s' % 'ex/gs objs runs med_s v0' for _ in args))
for pc in pcs:
    nm = names.get(pc, ('?', 0, ''))
    cells = []
    for p in args:
        o = res[p][2].get(pc)
        if not o: cells.append('%-30s' % '-'); continue
        n, rate, objs, durs, v0 = o
        cells.append('%-30s' % ('%6.1f %4d %4d %6s %s' % (rate, objs, len(durs), '%.3f' % st.median(durs) if len(durs) >= min_runs else '-',
                                                          st.median(v0) if len(v0) >= min_runs else '-')))
    print('%08X   %-40s %+4d | ' % (pc, nm[0][:40], nm[1]) + ' | '.join(cells))
