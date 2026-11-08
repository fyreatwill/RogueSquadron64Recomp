#!/usr/bin/env python3
"""s6990 G1e: per-level real game frame rate from one quiet-arm run (log + ROGUESQ_PRESENT_RING), one row per arm.
tasks = [g1b] gfx tasks/s (game frames submitted), t >= --from. From the ring over the same wall span (ring t0 + --from):
Q/s = presents queued, gen/s = distinct framebuffer generations queued, shown/s = distinct gens whose present reached glass
(P at>0, joined on mtl), rep% = queued presents repeating the previous present's gen (H-dup), miss/s = on-glass P->P >= 25 ms.
sd50/sd90 (s6991) = [g1b] sd_wall p50/p90 ms over the same window: gfx RSP host cost per task, a dense-3D-scene marker
(menus/title read ~1 ms, flight 7-10 ms), so a window spent in a menu or black load screen shows up.
cur (s6991) = level the level-select cursor actually opened on = log2 of the first [lvsel] init cursorMask; it must
equal lvl, else the arm flew another level (FORCE_UNLOCK clamp, see tools/g1e_owner_quiet_arms.zsh).
usage: g1e_level_fps.py DIR ARM... [--from 95]   (DIR holds log_<ARM>.txt and ring_<ARM>.txt)"""
import re, sys, statistics as st
a = sys.argv[1:]; frm = 95.0
if '--from' in a: i = a.index('--from'); frm = float(a[i+1]); del a[i:i+2]
d, arms = a[0], a[1:]
G = re.compile(rb'^\[g1b\] t=(\d+) vi=(\d+) tasks=(\d+)(?: sd_wall=([\d.]+))?')
pc = lambda v, p: sorted(v)[int(p*(len(v)-1))] if v else 0
print('arm   lvl cur mission crash | tasks mean p10 min | Q/s gen/s shown/s rep% miss/s | span_s sd50 sd90')
for A in arms:
    cur = '?'; tk = []; sd = []; lvl = '?'; fps = '?'; mi = 0; cr = 0
    try: L = open(f'{d}/log_{A}.txt', 'rb').read().split(b'\n')
    except OSError: print(A, 'no log'); continue
    for l in L:
        m = G.match(l)
        if m and int(m[1]) >= frm:
            tk.append(int(m[3]))
            if m[4]: sd.append(float(m[4]))
        if b'[saveslot]' in l and b'force=' in l and lvl == '?': lvl = re.search(rb'force=(-?\d+)', l)[1].decode()
        if cur == '?' and b'cursorMask)=0x' in l: cur = str(int(re.search(rb'cursorMask\)=0x([0-9A-Fa-f]+)', l)[1], 16).bit_length() - 1)
        if b'initMission' in l: mi += 1
        if re.search(rb'CRASH|SIGSEGV|SIGBUS|abort', l): cr += 1

    Q = {}; P = {}; t0 = None
    try:
        for l in open(f'{d}/ring_{A}.txt'):
            f = l.split()
            if not f: continue
            t = float(f[1]); t0 = t if t0 is None else t0
            if t - t0 < frm: continue
            kv = dict(x.split('=', 1) for x in f[2:] if '=' in x)
            if f[0] == 'Q' and 'mtl' in kv: Q[kv['mtl']] = (t, kv['gen'])
            elif f[0] == 'P' and 'mtl' in kv: P[kv['mtl']] = float(kv['at'])
    except OSError: pass
    qs = sorted(Q.values())
    span = (qs[-1][0] - qs[0][0]) if len(qs) > 1 else 0
    gens = [g for _, g in qs]; rep = sum(1 for i in range(1, len(gens)) if gens[i] == gens[i-1])
    shown = {Q[m][1] for m in Q if P.get(m, 0) > 0}
    on = sorted(P[m] for m in Q if P.get(m, 0) > 0); miss = sum(1 for i in range(1, len(on)) if on[i] - on[i-1] >= 0.025)
    r = lambda n: n / span if span else 0
    print(f'{A:5s} {lvl:>3s} {cur:>3s}{" !" if cur != lvl else "  "}{mi:6d} {cr:5d} | {st.mean(tk) if tk else 0:5.1f} {pc(tk,.1):4d} {min(tk) if tk else 0:4d} | '
          f'{r(len(qs)):4.1f} {r(len(set(gens))):5.1f} {r(len(shown)):7.1f} {100*rep/max(1,len(gens)-1):4.1f} {r(miss):6.2f} | {span:5.0f} {pc(sd,.5):4.1f} {pc(sd,.9):4.1f}')
