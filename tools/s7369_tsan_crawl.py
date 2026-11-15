#!/usr/bin/env python3
"""s7369: classify the TSan-arm 'crawl' at the 1024-wide scene from one ROGUESQ_G1E_TL ring + run.log.
Aligns each [stall-dump] (vi=N = N-th update_screen, code 3) to the TL clock, then for every inter-dump window reports
VI edges, update_screen calls, gfx kicks (5 arg 1), dp_complete (9), osViSwapBuffer (15) and when the first dp_complete
after the dump lands. Verdicts:
  H-slow   gfx work (kicks/dp_complete/swaps) continues at a low steady rate between dumps; the first post-dump completion
           is not tied to the dump instant (median lag > 1 s and spread)
  H-cycle2 kicks/completions are ~0 inside the 600-VI window and the first completion follows each dump within 0.5 s
Usage: s7369_tsan_crawl.py <tl.bin> <run.log> [--bin 10]"""
import struct, sys, re, argparse, collections, statistics as st
ap = argparse.ArgumentParser(); ap.add_argument('tl'); ap.add_argument('log'); ap.add_argument('--bin', type=float, default=10.0)
a = ap.parse_args()
raw = open(a.tl, 'rb').read(); n = len(raw) // 24
ev = sorted(e for e in ((lambda r: (r[0], r[1], r[2], r[4]))(struct.unpack_from('<qIIii', raw, i * 24)) for i in range(n)) if e[0])
t0 = ev[0][0]; T = lambda t: (t - t0) / 1e6
log = open(a.log, 'rb').read().decode('latin1')
dumps = [(int(m[0]), int(m[1]), int(m[2]), float(m[3])) for m in re.findall(r'\[stall-dump\] vi=(\d+) stalled_vi=(\d+) fs=(\d+).*?t=([\d.]+)', log)]
us = [e[0] for e in ev if e[1] == 3]
kind = {'vi': lambda e: e[1] == 1, 'us': lambda e: e[1] == 3, 'kick': lambda e: e[1] == 5 and e[2] == 1,
        'dpc': lambda e: e[1] == 9, 'swap': lambda e: e[1] == 15, 'rspexit': lambda e: e[1] == 7}
print(f'marks={n} span={T(ev[-1][0]):.1f}s update_screen={len(us)} dumps={len(dumps)}')
# per-bin rates over the whole run
nb = int(T(ev[-1][0]) // a.bin) + 1; B = {k: [0] * nb for k in kind}
for e in ev:
    b = int(T(e[0]) // a.bin)
    for k, f in kind.items():
        if f(e): B[k][b] += 1
print('bin_s ' + ' '.join(f'{k:>6}' for k in kind))
for i in range(nb): print(f'{i * a.bin:5.0f} ' + ' '.join(f'{B[k][i]:6d}' for k in kind))
# dump alignment: vi=N -> N-th update_screen mark (1-based); offset = elapsed t - TL time
lags = []; inwin = []
for vi, stalled, fs, te in dumps:
    if vi - 1 >= len(us): print(f'dump vi={vi} beyond ring'); continue
    td = us[vi - 1]; tw0 = us[max(0, vi - 1 - stalled)]
    win = {k: sum(1 for e in ev if tw0 <= e[0] < td and f(e)) for k, f in kind.items()}
    nxt = next((e[0] for e in ev if e[0] > td and e[1] == 9), None)
    nsw = next((e[0] for e in ev if e[0] > td and e[1] == 15), None)
    lag = (nxt - td) / 1e6 if nxt else None; lags.append(lag); inwin.append(win['dpc'] + win['kick'])
    print(f'dump vi={vi} stalled={stalled} fs={fs} t_log={te:.1f} t_tl={T(td):.1f} window={T(td) - T(tw0):.1f}s in-window {win} '
          f'next_dpc_lag={lag if lag is None else round(lag, 3)} next_swap_lag={None if nsw is None else round((nsw - td) / 1e6, 3)}')
L = [x for x in lags if x is not None]
if L:
    med = st.median(L)
    print(f'median next-dpc lag {med:.3f}s min {min(L):.3f} max {max(L):.3f}; in-window gfx marks {inwin}')
    if med < 0.5 and max(inwin) == 0: print('VERDICT H-cycle2')
    elif max(inwin) > 0 or med > 1.0: print('VERDICT H-slow (gfx work continues inside the stall windows / completion not tied to the dump)')
    else: print('VERDICT ?')
