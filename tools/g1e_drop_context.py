#!/usr/bin/env python3
"""s6974: context of every drain drop (D row) in a present ring after --from s.
Per drop: the --n shown Q rows before it (dQ = Q-to-Q ms, W phase of the Q after vsync, wl/acq/gpu/tp ms, lat = P at - Q + tp)
and --after rows after it; then a per-drop verdict line and a per-ring summary that splits the hypotheses:
  H-drain : the acq>5 run before the drop starts while lat is still at base (< --base+5) and no Q gap / gpu spike precedes it
            (acquire waits went up without the frame queue having deepened: a false fire on slow acquires)
  H-hitch : a Q-to-Q gap > 16.7+--hitch ms (late game frame) within the --n rows before the run start
  H-gpu   : a wl/gpu spike (> --gpu ms) within the --n rows before the run start
  real    : lat already >= base+5 at the run start (a level had formed: the drain was right)
usage: g1e_drop_context.py [--from 95] [--n 12] [--after 4] [--quiet] ring..."""
import argparse, statistics as st
ap = argparse.ArgumentParser(); ap.add_argument('rings', nargs='+')
ap.add_argument('--from', dest='frm', type=float, default=95); ap.add_argument('--n', type=int, default=12)
ap.add_argument('--after', type=int, default=4); ap.add_argument('--hitch', type=float, default=6.7)
ap.add_argument('--gpu', type=float, default=12); ap.add_argument('--quiet', action='store_true'); a = ap.parse_args()
VI = 1000 / 60
for path in a.rings:
    Q = []; P = {}; D = []; W = []; t0 = None
    for l in open(path, errors='replace'):
        p = l.split()
        if len(p) < 2 or not l.endswith('\n'): continue
        kv = dict(x.split('=', 1) for x in p[2:] if '=' in x)
        try:
            t = float(p[1]); t0 = t if t0 is None else t0; t -= t0
            if p[0] == 'D': D.append((t, kv.get('acq', '?')))
            elif p[0] == 'W': W.append(t)
            elif p[0] == 'Q' and kv.get('skip') == '0' and 'acq_ms' in kv:
                Q.append(dict(t=t, wl=float(kv['wl_ms']), acq=float(kv['acq_ms']), gpu=float(kv['gpu_ms']), tp=float(kv['tp_ms']), m=kv['mtl']))
            elif p[0] == 'P' and float(kv.get('at', 0)) > 0: P[kv['mtl']] = float(kv['at']) - t0
        except (KeyError, ValueError): pass
    for i, q in enumerate(Q):
        q['dq'] = (q['t'] - Q[i - 1]['t']) * 1e3 if i else 0
        q['lat'] = (P[q['m']] - q['t']) * 1e3 + q['tp'] if q['m'] in P else float('nan')
    sh = [q for q in Q if q['t'] >= a.frm and q['lat'] == q['lat']]
    base = st.median([q['lat'] for q in sh]) if sh else float('nan')
    print(f"=== {path}  base lat p50 {base:.1f} ms, {len(sh)} shown Q, {sum(t >= a.frm for t, _ in D)} drops after {a.frm:.0f} s")
    tally = {}
    for td, dacq in D:
        if td < a.frm: continue
        j = max((i for i, q in enumerate(Q) if q['t'] <= td), default=None)
        if j is None: continue
        r = j  # start of the consecutive acq>5 run ending at the drop
        while r > 0 and Q[r - 1]['acq'] > 5: r -= 1
        if Q[j]['acq'] <= 5: r = j
        win = Q[max(0, r - a.n):r + 1]
        lat0 = next((q['lat'] for q in Q[r:j + 1] if q['lat'] == q['lat']), float('nan'))
        gap = max((q['dq'] for q in win), default=0); spk = max((max(q['wl'], q['gpu']) for q in win), default=0)
        latpre = st.median([q['lat'] for q in win[:-1] if q['lat'] == q['lat']] or [float('nan')])
        tags = []
        if lat0 >= base + 5: tags.append('real')
        if gap > VI + a.hitch: tags.append('H-hitch')
        if spk > a.gpu: tags.append('H-gpu')
        if not tags: tags.append('H-drain')
        for k in tags: tally[k] = tally.get(k, 0) + 1
        lat_after = [q['lat'] for q in Q[j + 1:j + 1 + 30] if q['lat'] == q['lat']]
        print(f"D t={td:7.2f} acqrun={j - r + 1} (D acq={dacq}) lat pre {latpre:.1f} at-run-start {lat0:.1f} after30 p50 "
              f"{st.median(lat_after) if lat_after else float('nan'):.1f}  max dQ {gap:.1f}  max wl/gpu {spk:.1f}  -> {'+'.join(tags)}")
        if not a.quiet:
            for q in Q[max(0, r - a.n):j + 1 + a.after]:
                mark = '>' if r <= Q.index(q) <= j else ('a' if Q.index(q) > j else ' ')
                print(f"   {mark} {q['t']:8.3f} dQ {q['dq']:5.1f} wl {q['wl']:5.2f} acq {q['acq']:5.2f} gpu {q['gpu']:5.2f} tp {q['tp']:5.2f} lat {q['lat']:5.1f}")
    print('  tally:', tally)
