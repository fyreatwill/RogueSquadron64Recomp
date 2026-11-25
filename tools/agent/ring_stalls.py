#!/usr/bin/env python3
"""s7458 class DN: stall score of a ROGUESQ_PRESENT_RING file (lib/rt64 plume_metal.cpp ~2075, rt64_present_queue.cpp Q rows).

usage: ring_stalls.py <ring[.zst]> [gap_s=30] [--end-wall <epoch_s>]
prints: vi_stalls30s=<n> max_gap_ms=<m> max_vihold_ms=<h> tail_ms=<t> rows=<r> max_animhold_ms=<a>   (rows=0 -> vi_stalls30s=na)

s7923: max_vihold_ms counts FROZEN holds only. A VI-origin hold > 2 s whose rows advance gen= (RDP work generation) on >= 90%
of row pairs is an ANIMATING single-buffered scene (the 1592-wide title, s7921/s7922: 17.3 s on every owner-recipe run), not
a freeze; it goes to max_animhold_ms instead. Before s7923 max_vihold_ms was the raw max including those (soak verdict lines
before s7923 read ~17300 on every run). vi_stalls30s is unchanged (raw holds >= gap_s still count). --selftest runs planted
controls (1 s frozen hold must count, 17 s animating hold must not) and exits 3 on failure.

A stall episode is any interval >= gap_s in which EITHER
  (a) no Q (present) row was written           -> the present path itself stopped (H-ring), or
  (b) Q rows kept coming but vi= (the VI origin the present showed) never changed -> the guest stopped swapping while the
      host re-presented the same frame (H-blind: a pure present-gap count misses this one).
Overlapping intervals are merged into one episode. --end-wall: the wall time the launcher saw the game still alive just
before SIGKILL; (end_wall - ring mtime) is the silent tail after the last flushed row (rows flush every 64, ~0.5 s), and a
tail >= gap_s is one more episode (a hung game writes nothing, so (a) alone could never see it). Pass it only for arms that
were alive at the end: a dead game's silent tail is a death, not a stall.
"""
import os, subprocess, sys

ANIM_MS, ANIM_FRAC = 2000.0, 0.9

def rows(path, with_gen=False):
    if path.endswith('.zst'):
        data = subprocess.run(['zstd', '-dc', path], capture_output=True).stdout.decode('latin-1')
    else:
        data = open(path, encoding='latin-1').read()
    for l in data.split('\n')[:-1]:       # a SIGKILLed ring may end mid-line: the element after the last '\n' is dropped
        if l.startswith('Q ') and ' vi=' in l:
            p = l.split()
            try:
                t = float(p[1]); vi = next(x[3:] for x in p if x.startswith('vi='))
                g = next((x[4:] for x in p if x.startswith('gen=')), None)
            except (ValueError, StopIteration):
                continue
            yield (t, vi, g) if with_gen else (t, vi)

def animating(G):
    """G: gen= values of the rows inside one hold. True when gen advances on >= ANIM_FRAC of row pairs."""
    if len(G) < 2: return False
    adv = sum(1 for a, b in zip(G, G[1:]) if b != a)
    return adv / (len(G) - 1) >= ANIM_FRAC

def score(path, gap_s=30.0, end_wall=None, Q=None):
    Q = list(rows(path, True)) if Q is None else Q
    if not Q:
        return dict(n='na', gap=0, hold=0, tail=0, rows=0, anim=0)
    iv = []; mg = 0.0; mh = 0.0; ma = 0.0
    for (t0, _, _), (t1, _, _) in zip(Q, Q[1:]):
        g = t1 - t0; mg = max(mg, g)
        if g >= gap_s: iv.append((t0, t1))
    s, v, _ = Q[0]; G = []
    for t, x, gn in Q + [(Q[-1][0], None, None)]:
        if x != v:
            h = t - s
            if h * 1e3 > ANIM_MS and animating(G): ma = max(ma, h)
            else: mh = max(mh, h)
            if h >= gap_s: iv.append((s, t))
            s, v, G = t, x, []
        G.append(gn)
    iv.sort(); n = 0; ce = None
    for a, b in iv:
        if ce is None or a > ce: n += 1; ce = b
        else: ce = max(ce, b)
    tail = 0.0
    if end_wall is not None:
        tail = max(0.0, end_wall - os.path.getmtime(path))
        if tail >= gap_s: n += 1
    return dict(n=n, gap=mg * 1e3, hold=mh * 1e3, tail=tail * 1e3, rows=len(Q), anim=ma * 1e3)

def selftest():
    """Planted controls: 60 Hz rows; a 1 s hold with gen frozen, a 17 s hold with gen advancing every row, a 3 s hold with
    gen advancing on only half the rows (frozen-ish: must count), then normal flipping."""
    def build(with_e):
        Q = []; st = [0.0, 0]
        def run(n, vi, step):
            for i in range(n):
                Q.append((st[0], vi, str(st[1]))); st[0] += 1 / 60.0; st[1] += step(i)
        for k in range(60): run(1, 'A' if k % 2 else 'B', lambda i: 1)
        run(60, 'C', lambda i: 0)                     # 1.0 s frozen
        run(1020, 'D', lambda i: 1)                   # 17 s animating
        if with_e: run(180, 'E', lambda i: i % 2)     # 3 s, gen advances on 50%
        for k in range(60): run(1, 'A' if k % 2 else 'B', lambda i: 1)
        return Q
    r = score(None, 30.0, None, build(True))
    ok = 2950 <= r['hold'] <= 3050 and 16950 <= r['anim'] <= 17050
    r2 = score(None, 30.0, None, build(False))        # without E, the 1 s frozen hold is the max
    ok = ok and 950 <= r2['hold'] <= 1050 and 16950 <= r2['anim'] <= 17050
    print('selftest %s: hold=%.0f anim=%.0f | no-E hold=%.0f anim=%.0f' % ('PASS' if ok else 'FAIL', r['hold'], r['anim'], r2['hold'], r2['anim']))
    return ok

if __name__ == '__main__':
    a = sys.argv[1:]; ew = None
    if '--end-wall' in a:
        i = a.index('--end-wall'); ew = float(a[i + 1]); del a[i:i + 2]
    if a == ['--selftest']:
        sys.exit(0 if selftest() else 3)
    if not a:
        sys.exit(__doc__)
    gap = float(a[1]) if len(a) > 1 else 30.0
    if not os.path.exists(a[0]):
        print('vi_stalls30s=na max_gap_ms=0 max_vihold_ms=0 tail_ms=0 rows=0 max_animhold_ms=0'); sys.exit(0)
    r = score(a[0], gap, ew)
    print(f"vi_stalls30s={r['n']} max_gap_ms={r['gap']:.0f} max_vihold_ms={r['hold']:.0f} tail_ms={r['tail']:.0f} rows={r['rows']} max_animhold_ms={r['anim']:.0f}")
