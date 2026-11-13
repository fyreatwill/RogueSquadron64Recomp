#!/usr/bin/env python3
"""s7233 G1c: score a ROGUESQ_DD_WIDEWIN_R=<R> + _R_TOG=1 run (build >= s7233: [g1cf] carries wr=<R in force>, [s7233] tallies).
Per log: [g1cf] VI lines split by wr (0 = R off, >0 = R on), binned to [g1b] seconds as in s7232_tri_onscreen.py; reports per task
tri/tin/tzero/kpx for the window (--t0..--t1) and the flight, on vs off, and the delta. sd_wall per arm uses only seconds whose VIs
are >= --pure (default 0.8) one arm. [s7233] lines: wide-only non-empty cells per placement by 8-cell eye-distance bin, skipped per
placement (positive control: skip > 0 on ph=1, 0 on ph=0; in = retail-equivalent window cells, must match across phases).
Usage: s7233_widewin_r.py log_r40.txt [log_r56.txt ...] [--t0 77 --t1 97]"""
import re, sys, os, argparse
ap = argparse.ArgumentParser(); ap.add_argument('logs', nargs='+')
ap.add_argument('--t0', type=int, default=77); ap.add_argument('--t1', type=int, default=97)
ap.add_argument('--flight0', type=int, default=60); ap.add_argument('--flight1', type=int, default=230)
ap.add_argument('--pure', type=float, default=0.8)
ap.add_argument('--merge', action='store_true', help='s7240: split on/off by [g1cf] wm= (WIDEWIN_MERGE phase) and use the [s7239] control')
a = ap.parse_args()
G1B = re.compile(r'\[g1b\] t=(\d+) vi=\d+ tasks=(\d+) sd_wall=([\d.]+)/')
G1CF = re.compile(r'\[g1cf\] vi=\d+ dd=\d+ tasks=(\d+) .*? tri=(\d+) .*? tin=(\d+) tout=(\d+) tzero=(\d+) vout=(\d+) kpx=([\d.]+) '
                  r'sc=\S+ bin=\S+ wr=(-?\d+)(?: wm=(\d+))?')
S7239 = re.compile(r'\[s7239\] ph=(\d) ')
S7233 = re.compile(r'\[s7233\] ph=(\d) r=(\d+) calls=\d+ in=([\d.]+) skip=([\d.]+) wide_by_d8=([\d.,]+)')
K = ['tasks', 'tri', 'tin', 'tzero', 'kpx']
bad = 0
for p in a.logs:
    lab = os.path.basename(p).split('.')[0]; vis = []; secs = []; cur = []; tl = {0: [], 1: []}; tm = {0: [], 1: []}
    for ln in open(p, errors='ignore'):
        m = G1CF.match(ln)
        if m: cur.append(dict(zip(K, [int(m[1]), int(m[2]), int(m[3]), int(m[5]), float(m[7])]), on=int(int(m[9] or 0) > 0) if a.merge else int(int(m[8]) > 0))); continue
        m = G1B.match(ln)
        if m:
            t = int(m[1])
            for v in cur: v['t'] = t
            vis += cur
            if cur: secs.append((t, float(m[3]), sum(v['on'] for v in cur) / len(cur)))
            cur = []; continue
        m = S7239.match(ln)
        if m:
            d = {k: int(v) for k, v in re.findall(r'(\w+)=(\d+)(?=\s|$)', ln)}
            h = re.search(r' dh=([\d,]+)', ln)  # s7246 edge-deviation histogram, bins <=0,8,16,32,64,128,256,inf (emitted units)
            if h: d['dh'] = [int(x) for x in h[1].split(',')]
            tm[int(m[1])].append(d); continue
        m = S7233.match(ln)
        if m: tl[int(m[1])].append((float(m[3]), float(m[4]), [float(x) for x in m[5].split(',')]))
    print(f'== {lab}: VIs {len(vis)}  [s7233] blocks ph0 {len(tl[0])} ph1 {len(tl[1])}')
    # s7236 positive control: ph1 must skip cells and ph0 must not, else the arm is not evidence (null without control)
    ctl = bool(tl[1]) and bool(tl[0]) and sum(x[1] for x in tl[1]) > 0 and sum(x[1] for x in tl[0]) == 0
    if a.merge:  # s7240 control: ph1 merges (drops == 3x merged, 0 unmerged anchors), ph0 finds candidates but merges none
        S = {ph: {k: sum(d.get(k, 0) for d in tm[ph]) for k in ('grp', 'noww', 'flag', 'el', 'flat', 'cand', 'anc', 'drop', 'merged', 'ovf', 'miss', 'near', 'unm', 'dup', 'stale')} for ph in (0, 1)}
        for ph in (0, 1): print(f'  [s7239] ph{ph} lines={len(tm[ph])} ' + ' '.join(f'{k}={v}' for k, v in S[ph].items()))
        for ph in (0, 1):  # s7246 flatness gate summary
            dh = [sum(d.get('dh', [0] * 8)[i] for d in tm[ph]) for i in range(8)]; n = max(sum(dh), 1)
            E = next((d['E'] for d in tm[ph] if 'E' in d), None)
            print(f'  s7246 ph{ph} E={E} flatrej={sum(d.get("flatrej", 0) for d in tm[ph])} ctrrej={sum(d.get("ctrrej", 0) for d in tm[ph])} '
                  f'shmis={sum(d.get("shmis", 0) for d in tm[ph])} dev-cum<=0/8/16/32/64/128/256: ' + ' '.join(f'{sum(dh[:i + 1]) / n:.3f}' for i in range(7)) + f' (n={sum(dh)})')
        ctl = S[1]['merged'] > 0 and S[1]['drop'] == 3 * S[1]['merged'] and S[1]['unm'] == 0 and S[0]['anc'] == 0 and S[0]['drop'] == 0 and S[0]['cand'] > 0
        print(f'  merge: drops/merged={S[1]["drop"] / max(S[1]["merged"], 1):.2f} (3.00 expected); tri removed per merged block expected ~6')
    win = [v for v in vis if a.t0 <= v['t'] <= a.t1 - 1 and v['tasks'] > 0]
    print(f'  CONTROL {"PASS" if ctl else "FAIL"} (ph1 skip>0, ph0 skip=0)  window VIs={len(win)}{"" if win else " (WINDOW NOT REACHED)"}')
    bad |= (not ctl) or (not win)
    for ph in (0, 1):
        L = tl[ph]
        if not L: continue
        n = len(L); h = [sum(x[2][i] for x in L) / n for i in range(17)]
        print(f'  [s7233] ph{ph}: in={sum(x[0] for x in L)/n:.0f} skip={sum(x[1] for x in L)/n:.0f} wide cells/placement by d8: ' +
              ' '.join(f'{8*i}:{v:.0f}' for i, v in enumerate(h) if v >= 0.5))
    summ = {}
    for name, lo, hi in (('window', a.t0, a.t1 - 1), ('flight', a.flight0, a.flight1)):
        res = {}
        for on in (0, 1):
            L = [v for v in vis if lo <= v['t'] <= hi and v['on'] == on and v['tasks'] > 0]
            T = sum(v['tasks'] for v in L) or 1
            d = {k: sum(v[k] for v in L) / T for k in K[1:]}; d['n'] = len(L)
            S = [s for s in secs if lo <= s[0] <= hi and (s[2] >= a.pure if on else s[2] <= 1 - a.pure)]
            d['sd'] = sum(s[1] for s in S) / max(len(S), 1); d['ns'] = len(S); res[on] = d
            print(f'  {name:6s} R{"on " if on else "off"} VIs={d["n"]:4d} pure_s={d["ns"]:3d} sd={d["sd"]:.2f}ms per task: tri={d["tri"]:.0f} '
                  f'tin={d["tin"]:.0f} tzero={d["tzero"]:.0f} kpx={d["kpx"]:.0f}')
        x, y = res[1], res[0]
        print(f'  {name:6s} on-off: dsd={x["sd"]-y["sd"]:+.2f}ms dtri={x["tri"]-y["tri"]:+.0f} dtin={x["tin"]-y["tin"]:+.0f} '
              f'dtzero={x["tzero"]-y["tzero"]:+.0f} dkpx={x["kpx"]-y["kpx"]:+.1f} ({(x["kpx"]-y["kpx"])/max(y["kpx"],1e-9):+.1%})')
        # s7238: triangles removed per skipped cell (level-2 retail mesh = one 4-corner quad per cell, so <= 2 when the cell
        # is the unit of cost) and ms per 1000 removed tris (s7231 pooled slope 1.80)
        sk = sum(x_[1] for x_ in tl[1]) / max(len(tl[1]), 1); dt = y["tri"] - x["tri"]
        print(f'  {name:6s} s7238: tri_per_skipped_cell={dt / max(sk, 1e-9):.2f} ms_per_ktri={(y["sd"] - x["sd"]) / max(dt / 1000, 1e-9):.2f}')
        summ[name] = (x["sd"] - y["sd"], (x["kpx"] - y["kpx"]) / max(y["kpx"], 1e-9))
    # s7238 decision bar (NEXT s7237): H-radius met when window dsd <= -2.5 ms and flight |dkpx| <= 1%
    w, f = summ.get('window', (0, 0)), summ.get('flight', (0, 0))
    print(f'  s7238 BAR {"MET" if w[0] <= -2.5 and abs(f[1]) <= 0.01 else "not met"} (window dsd {w[0]:+.2f} ms, flight dkpx {f[1]:+.1%})')
sys.exit(3 if bad else 0)
