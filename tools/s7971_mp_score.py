#!/usr/bin/env python3
"""s7971 class MP scorer: one arm of tools/s7971_mp_e2e.zsh (host memory pressure window [press_start, press_end] ms after
launch; the game's ring/AI clock is seconds since launch, so the window maps directly, error < 0.5 s).

usage: s7971_mp_score.py <ring> <ai_trace> <log> <press_start_ms> <press_end_ms> [<vm_samples>]   |   --selftest

Windows: base = 30 s before the press, press = the press window, post = 30 s after it. Per window: min presents/s, max present
gap, max VI-origin hold (animating single-buffered holds, gen advancing on >= 90% of rows, excluded as in s7923), AI posts
that found the SDL queue empty (underrun) per 10 s, min AI buffers/s. .vm: memorystatus level max and game RSS min in the
press window vs the base median (did the pressure reach the GAME's pages: rss_drop_mb).
verdict: crash     a crash/abort line or an [RT64]/Metal allocation failure line
         stall     press/post max present gap > max(250 ms, 2x base) or a VI hold > 1 s
         underrun  press/post empty-queue AI posts per 10 s > base + 3
         noalign   uptime-stamped ring with < 5 framebuffers shared with the AI trace (cannot place the window)
         moot      none of the above
"""
import re, sys, statistics
# zst-ok: reads the .ai/.log/.vm s7971_mp_e2e.zsh keeps raw (ring via s7970 qrows, which decompresses .zst)
sys.path.insert(0, __import__('os').path.dirname(__file__))
from s7970_sw_score import qrows, airows, ANIM_FRAC

def win(Q, A, a, b):
    r = {}
    q = [x for x in Q if a <= x[0] < b]
    ps = [sum(1 for x in q if a + i <= x[0] < a + i + 1) for i in range(int(b - a))]
    r['pres_min'] = min(ps) if ps else 0
    r['gap_ms'] = round(max([y[0] - x[0] for x, y in zip(q, q[1:])] or [0]) * 1e3, 1)
    hold = 0.0
    if q:
        s, v, G = q[0][0], q[0][1], []
        for t, x, g in q + [(q[-1][0], None, None)]:
            if x != v:
                adv = sum(1 for m, n in zip(G, G[1:]) if m != n)
                if not (len(G) > 1 and None not in G and adv / (len(G) - 1) >= ANIM_FRAC): hold = max(hold, t - s)
                s, v, G = t, x, []
            G.append(g)
    r['vihold_s'] = round(hold, 2)
    aa = [x for x in A if a <= x[0] < b]
    r['ai_zero10'] = round(sum(1 for t, qb in aa if qb == 0) * 10 / max(b - a, 1), 2)
    bs = [sum(1 for t, _ in aa if a + i <= t < a + i + 1) for i in range(int(b - a))]
    r['ai_min'] = min(bs) if bs else 0
    return r

def vmstats(path, a, b):
    r = {}
    try: rows = [dict(kv.split('=', 1) for kv in l.split()[1:] if '=' in kv) | {'t': int(l.split()[0]) / 1e3} for l in open(path) if l[:1].isdigit()]
    except OSError: return r
    def num(d, k):
        try: return float(d.get(k, ''))
        except ValueError: return None
    base = [num(d, 'rss_kb') for d in rows if a - 30 <= d['t'] < a and num(d, 'rss_kb')]
    pr = [d for d in rows if a <= d['t'] <= b]
    if base and pr:
        rm = [num(d, 'rss_kb') for d in pr if num(d, 'rss_kb')]
        r['rss_base_mb'] = round(statistics.median(base) / 1024); r['rss_press_min_mb'] = round(min(rm) / 1024) if rm else -1
        r['rss_drop_mb'] = r['rss_base_mb'] - r['rss_press_min_mb'] if rm else -1
        r['lvl_max'] = int(max(num(d, 'lvl') or 0 for d in pr)); r['vm_rows'] = len(pr)
    return r

def align(Q, aipath):
    """The present ring (Q rows) is stamped in host steady_clock seconds (uptime), the AI trace in seconds since launch.
    Offset = median over VI framebuffers of (first Q row presenting it - first AI row committing it); the AI trace logs the
    VI origin register = framebuffer base + one scanline (2 x width bytes), the ring the base. Returns (offset, n, spread)."""
    fa = {}
    try:
        for l in open(aipath, encoding='latin-1'):
            p = l.split()
            if len(p) >= 5:
                try: fa.setdefault(f'{int(p[4], 16) - 2 * int(p[3]):06X}', float(p[0]))
                except ValueError: pass
    except OSError: return 0.0, 0, 0.0
    fq = {}
    for t, v, g in Q: fq.setdefault(v, t)
    d = sorted(fq[k] - fa[k] for k in fa if k in fq)
    if not d: return 0.0, 0, 0.0
    m = statistics.median(d); return m, len(d), round(m - d[0], 3)

def score(Q, A, log, ps, pe, vm=None, aipath=None):
    if len(Q) < 100: return dict(verdict='noring', rows=len(Q))
    r = {}
    if aipath and Q[0][0] > 1e3:  # uptime-stamped ring: move it onto the launch clock
        off, n, spr = align(Q, aipath); r['align_n'] = n; r['align_spread_s'] = spr; r['ring_t0_s'] = round(Q[0][0] - off, 2)
        if n < 5: return r | dict(verdict='noalign')
        Q = [(t - off, v, g) for t, v, g in Q]
    W = {'base': (ps - 30, ps), 'press': (ps, pe), 'post': (pe, pe + 30)}
    w = {k: win(Q, A, *v) for k, v in W.items()}
    for k, d in w.items():
        for f, v in d.items(): r[f'{k}_{f}'] = v
    if vm: r |= vmstats(vm, ps, pe)
    L = log.split('\n')
    r['crashlines'] = sum(1 for l in L if re.search(r'CRASH|SIGSEGV|SIGBUS|SIGABRT|terminate called|Assertion failed|abort\(', l))
    r['allocfail'] = sum(1 for l in L if re.search(r'(?i)(\[RT64\]|metal).*(fail|nil|out of memory)|newBuffer.*fail|std::bad_alloc', l))
    gl = max(250.0, 2 * w['base']['gap_ms'])
    v = 'moot'
    if r['crashlines'] or r['allocfail']: v = 'crash'
    elif any(w[k]['gap_ms'] > gl or w[k]['vihold_s'] > 1.0 for k in ('press', 'post')): v = 'stall'
    elif any(w[k]['ai_zero10'] > w['base']['ai_zero10'] + 3 for k in ('press', 'post')): v = 'underrun'
    r['verdict'] = v
    return r

def fmt(r): return ' '.join(f'{k}={v}' for k, v in r.items())

def selftest():
    def ring(gap_at=None, gap=0.0, hold_at=None):
        Q = []; t = 3.0; k = 0
        while t < 250:
            t += 1 / 60
            if gap_at and abs(t - gap_at) < 0.01: t += gap
            if not (hold_at and hold_at <= t < hold_at + 2): k += 1
            Q.append((t, f'{k:06X}', None))
        return Q
    def ai(zero_at=None):
        return [(3 + i * 0.033, 0 if zero_at and zero_at <= 3 + i * 0.033 < zero_at + 3 else 4000) for i in range(7400)]
    cases = [('moot', ring(), ai(), ''), ('stall', ring(gap_at=150, gap=0.6), ai(), ''), ('stall', ring(hold_at=190), ai(), ''),
             ('underrun', ring(), ai(zero_at=160), ''), ('crash', ring(), ai(), '[RT64] newBuffer failed: out of memory'),
             ('crash', ring(), ai(), 'CRASH SIGSEGV'), ('moot', ring(gap_at=110, gap=0.6), ai(zero_at=100), '')]  # pre-window events ignored
    # uptime-stamped ring (the real format): +116000 s offset, AI file logs origin = base + 2 x 320. Aligned -> the planted
    # 0.6 s gap at game t=150 is seen (stall); without the AI path the window is empty and reads moot (alignment matters).
    import tempfile
    Qu = [(t + 116000.0, f'{(int(v, 16) % 8) * 0x40000 + 0x100000:06X}', g) for t, v, g in ring(gap_at=150, gap=0.6)]
    fd, ap = tempfile.mkstemp(suffix='.ai')
    with open(fd, 'w') as f:
        for t, v, g in Qu: f.write(f'{t - 116000.0 - 0.01:.4f} 4000 384 320 {int(v, 16) + 640:06X} 0\n')
    ok = True
    for want, path in (('stall', ap), ('moot', None)):
        got = score(Qu, ai(), '', 125.0, 185.0, None, path)['verdict']; ok &= got == want; print(f'selftest want={want} got={got} (uptime ring, ai={"yes" if path else "no"})')
    __import__('os').unlink(ap)
    for want, Q, A, lg in cases:
        got = score(Q, A, lg, 125.0, 185.0)['verdict']; ok &= got == want; print(f'selftest want={want} got={got}')
    print('SELFTEST', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 3)

if __name__ == '__main__':
    if '--selftest' in sys.argv: selftest()
    ring, ai, logf, ps, pe = sys.argv[1:6]; vm = sys.argv[6] if len(sys.argv) > 6 else None
    try: lg = open(logf, encoding='latin-1').read()
    except OSError: lg = ''
    print(fmt(score(qrows(ring), airows(ai), lg, float(ps) / 1e3, float(pe) / 1e3, vm, ai)))
