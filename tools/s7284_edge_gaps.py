#!/usr/bin/env python3
"""s7284 G5c load-edge gap classifier (offline, no game run).
For every s7277-style toggle run (scratch/s7277/ring_<TAG>.txt + <TAG>.toggle + <TAG>.ctl) list every new-fb-gen gap
>= MIN ms (default 250) with: absolute run time, the load window it starts in (pre = route before the first toggle, on, off),
the time since the last toggle edge and that edge's kind (on->off / off->on), the load type (cpu / gpu + GPU_ITER), and, when the
s7272 hold sheet exists (scratch/s7272/<TAG>/sheet.txt, capture-relative times), the held frame luma of the matching image hold
(capture clock aligned to the ring clock through the SIGSTOP control windows, which both clocks record).
Class per gap: CTL (inside a SIGSTOP control +-3 s: the positive control, must appear), PRE (route/loading before the first
window), ON (inside a load window), EDGE (off window, <= EDGE_S s after an on->off edge), QUIET (off window, > EDGE_S from the last
edge). QUIET gaps with held luma < 10 are tagged black (transition frame), else -fbsw when the fb double-buffer pair relocates
across the gap (scene change; s7284: L4 restart sequence B51E00/AA3C00 -> A7CA00/A12600, ~2.6 s before its black hold), else lit
(a candidate real quiet-host freeze). Any gap with FBSWITCH in its line is a relocation, whatever its class.
usage: s7284_edge_gaps.py [TAG ...]   (default: every ring_*.txt in scratch/s7277)   env MIN=250 EDGE_S=2"""
import glob, os, re, sys
D = 'scratch/s7277'; SH = 'scratch/s7272'
MIN = float(os.environ.get('MIN', 250)); EDGE_S = float(os.environ.get('EDGE_S', 2))
tags = sys.argv[1:] or sorted(re.sub(r'^ring_|\.txt$', '', os.path.basename(p)) for p in glob.glob(f'{D}/ring_*.txt'))

def gpu_iter(tag):
    m = re.search(r'i(\d+)$', tag)
    if m: return int(m.group(1))
    return 80000 if tag.startswith('l12cb') else 20000

def load_type(tag):
    return f'gpu/{gpu_iter(tag)}' if ('gpu' in tag or tag.startswith('l12cb') or os.path.exists(f'{D}/{tag}.gpu')) else 'cpu'

tot = {}
for T in tags:
    try:
        ev = [(l.split()[0], float(l.split()[1])) for l in open(f'{D}/{T}.toggle') if l.strip()]
    except OSError:
        print(f'{T}: no toggle file, skipped'); continue
    try: ctl = [(int(a)/24e6, int(b)/24e6) for a, b in (l.split() for l in open(f'{D}/{T}.ctl') if l.strip())]
    except OSError: ctl = []
    gens = []; fbs = []; last = None
    for l in open(f'{D}/ring_{T}.txt'):
        if not l.startswith('Q '): continue
        f = l.split(); g = next((x[4:] for x in f[2:] if x.startswith('gen=')), None)
        fb = next((x[3:] for x in f[2:] if x.startswith('fb=')), None)
        if g != last: gens.append(float(f[1])); fbs.append(fb); last = g
    if not gens: print(f'{T}: empty ring'); continue
    t0 = gens[0]
    # hold sheet alignment: capture-relative control times vs ring-clock ctl starts
    holds = []
    sp = f'{SH}/{T}/sheet.txt'
    if os.path.exists(sp) and ctl:
        rows = []
        for l in open(sp):
            m = re.match(r'\+([\d.]+)s (\d+)ms ph\d ctl=(\d) luma pre/held/next/post (\d+) (\d+) (\d+) (\d+)', l)
            if m: rows.append((float(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(5))))
        cr = [r[0] for r in rows if r[2] == 1]
        if cr:
            off = sum(c[0] - r for c, r in zip(ctl, cr)) / min(len(ctl), len(cr))
            holds = [(r[0] + off, r[1], r[3]) for r in rows]
    edges = [(ev[k][1], f'{ev[k-1][0]}->{ev[k][0]}') for k in range(1, len(ev))]
    lt = load_type(T); c = {}
    print(f'== {T} load {lt} span {gens[-1]-t0:.0f} s windows {len(ev)} first toggle +{ev[0][1]-t0:.0f} s sheet {"yes" if holds else "no"}')
    for i in range(len(gens) - 1):
        gap = (gens[i+1] - gens[i]) * 1000
        if gap < MIN: continue
        a = gens[i]
        if any(x - 3 <= a <= y + 3 or x - 3 <= gens[i+1] <= y + 3 for x, y in ctl): cls = 'CTL'
        elif a < ev[0][1]: cls = 'PRE'
        else:
            st = [s for s, t in ev if t <= a][-1]
            if st == 'on': cls = 'ON'
            else:
                le = max(t for t, k in edges if t <= a) if any(t <= a for t, k in edges) else ev[0][1]
                cls = 'EDGE' if a - le <= EDGE_S else 'QUIET'
        pe = [(t, k) for t, k in edges if t <= a + 0.5]
        el = f'{pe[-1][1]} {a-pe[-1][0]:+.2f}s' if pe else 'before first edge'
        h = min(holds, key=lambda r: abs(r[0] - a), default=None)
        hs = f'luma {h[2]:3d} hold {h[1]} ms (dt {h[0]-a:+.2f})' if h and abs(h[0] - a) < 1.0 else 'no sheet hold'
        # fb relocation: the double-buffer pair after the gap shares no address with the pair before it (scene change)
        fbsw = not (set(fbs[max(0, i-3):i+1]) & set(fbs[i+1:i+5]))
        if fbsw: hs += ' FBSWITCH'
        if cls == 'QUIET' and h and abs(h[0] - a) < 1.0: cls += '-black' if h[2] < 10 else '-lit'
        elif cls == 'QUIET' and fbsw: cls += '-fbsw'
        c[cls] = c.get(cls, 0) + 1; tot[cls] = tot.get(cls, 0) + 1
        print(f'  +{a-t0:7.2f}s {gap:6.0f} ms {cls:11} last edge {el:22} {hs}')
    print(f'  counts {dict(sorted(c.items()))}')
print(f'ALL counts {dict(sorted(tot.items()))}  (MIN {MIN:.0f} ms, EDGE_S {EDGE_S} s)')
