#!/usr/bin/env python3
"""s7285 G5c gap decomposition (offline, no game run): for every new-fb-gen gap >= MIN ms in the s7277-style present rings
(scratch/s7277/ring_<TAG>.txt) split the gap into its sides using all three row kinds:
  Q = a VI present request served by the present thread (one per VI when the guest asks); W = a guest workload (display list)
      finished rendering on the RT64 workload thread; gen = the fb generation the shown Q row displays.
Per gap: nQ, max Q->Q interval (present stalled?), max tp/acq/gpu ms of Q rows in or just after the gap (present-side cost),
nW, max W->W interval (guest produced no display list?), and the fbs the W rows drew.
Class: GUEST-IDLE   no W rows for >= 80% of the gap (the guest submitted no gfx: CPU-side load work / audio wait / stopped);
       PRESENT-STALL W rows keep coming but no Q row for >= 80% of the gap, or a post-gap Q row with tp/acq/gpu >= 50% of it;
       HIDDEN-DRAW  W and Q rows keep flowing but the shown gen does not advance (the guest draws buffers the VI does not show);
       MIXED otherwise.
Positive control: SIGSTOP control windows (TAG.ctl) stop the whole process -> must classify GUEST-IDLE with no Q rows either.
usage: s7285_gap_split.py [TAG ...]  env MIN=250 FBSW_ONLY=0 (1 = only FBSWITCH + CTL gaps)"""
import glob, os, re, sys
D = 'scratch/s7277'
MIN = float(os.environ.get('MIN', 250)); FO = os.environ.get('FBSW_ONLY', '0') == '1'
tags = sys.argv[1:] or sorted(re.sub(r'^ring_|\.txt$', '', os.path.basename(p)) for p in glob.glob(f'{D}/ring_*.txt'))
kv = lambda f: dict(x.split('=', 1) for x in f[2:] if '=' in x)
tot = {}; rows_all = []
for T in tags:
    try: ctl = [(int(a)/24e6, int(b)/24e6) for a, b in (l.split() for l in open(f'{D}/{T}.ctl') if l.strip())]
    except OSError: ctl = []
    Q = []; W = []
    for l in open(f'{D}/ring_{T}.txt'):
        f = l.split()
        if not f: continue
        if f[0] == 'Q': Q.append((float(f[1]), kv(f)))
        elif f[0] == 'W': W.append((float(f[1]), kv(f)))
    if not Q: continue
    Q.sort(key=lambda r: r[0]); W.sort(key=lambda r: r[0])
    gens = []; last = None
    for i, (t, d) in enumerate(Q):
        if d.get('gen') != last: gens.append(i); last = d.get('gen')
    t0 = Q[0][0]; c = {}
    print(f'== {T}')
    for a, b in zip(gens, gens[1:]):
        ta, tb = Q[a][0], Q[b][0]; gap = (tb - ta) * 1e3
        if gap < MIN: continue
        fbA = {Q[k][1].get('fb') for k in gens[max(0, gens.index(a)-3):gens.index(a)+1]}
        fbB = {Q[k][1].get('fb') for k in gens[gens.index(b):gens.index(b)+4] if k < len(Q)}
        fbsw = not (fbA & fbB)
        isctl = any(x - 3 <= ta <= y + 3 or x - 3 <= tb <= y + 3 for x, y in ctl)
        if FO and not (fbsw or isctl): continue
        qt = [ta] + [t for t, _ in Q[a+1:b]] + [tb]; nq = len(qt) - 2
        mq = max(y - x for x, y in zip(qt, qt[1:])) * 1e3
        wt = [t for t, _ in W if ta < t < tb]; nw = len(wt)
        mw = max(y - x for x, y in zip([ta] + wt + [tb], wt + [tb])) * 1e3
        post = Q[b][1]; cost = max(float(post.get(k, 0)) for k in ('tp_ms', 'acq_ms', 'gpu_ms'))
        incost = max([max(float(d.get(k, 0)) for k in ('tp_ms', 'acq_ms', 'gpu_ms')) for _, d in Q[a+1:b+1]] or [0])
        wfb = sorted({x for t, d in W if ta < t < tb for x in d.get('fbs', '').split(',') if x})
        if mw >= 0.8 * gap: cls = 'GUEST-IDLE'
        elif mq >= 0.8 * gap or cost >= 0.5 * gap: cls = 'PRESENT-STALL'
        elif nw and nq: cls = 'HIDDEN-DRAW'
        else: cls = 'MIXED'
        key = ('CTL ' if isctl else '') + cls
        c[key] = c.get(key, 0) + 1; tot[key] = tot.get(key, 0) + 1
        rows_all.append((T, ta - t0, gap, key, nq, mq, nw, mw, incost, fbsw))
        print(f'  +{ta-t0:7.2f}s {gap:6.0f} ms {key:18} nQ {nq:3d} maxQQ {mq:6.0f}  nW {nw:3d} maxWW {mw:6.0f}  '
              f'Qcost max {incost:6.1f} ms  {"FBSW" if fbsw else "    "} Wfbs {",".join(wfb[:4])}{"..." if len(wfb) > 4 else ""}')
    print(f'  counts {dict(sorted(c.items()))}')
print(f'ALL counts {dict(sorted(tot.items()))}  (MIN {MIN:.0f} ms)')
