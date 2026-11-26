#!/usr/bin/env python3
"""s7970 class SW scorer: one arm of tools/s7970_sw_e2e.zsh (game SIGSTOPped for <stop_s>, then SIGCONT).

usage: s7970_sw_score.py <ring> <ai_trace> <log> <stop_s> [stop_at_s]      |   --selftest (planted controls, exit 3 on failure)

The resume point is the largest gap between present (Q) rows; for stop_s > 0 it must be stop_s +-3 s (anchor_ok=1), else
the stop never reached the ring (anchor_ok=0 -> verdict=noanchor). For stop_s == 0 (control arm) the largest gap is used
too; it is a normal frame. Base = the 10 s before the last pre-stop row, post = the 30 s after it. Per 1 s window: presents (Q rows) and
VI-origin changes (game swaps). The AI trace (one row per AI buffer: t, SDL queue bytes before, samples) gives buffers per
1 s window and the max queue depth after the anchor. Log: [s7199-hotplug] reopen lines, crash/abort lines.
verdict: crash   a crash/abort line
         burst   any post window with presents or swaps > 1.5x the base max (+3), or AI buffers > 2x base max (+3)
         stall   VI origin frozen > 5 s after the anchor, or no present row in the 30 s after it
         reopen  an audio device reopen whose why= is not resume (spurious stall watchdog fire; why=resume is the s7970 fix)
         moot    none of the above
"""
import re, subprocess, sys
ANIM_FRAC = 0.9  # s7923 (tools/agent/ring_stalls.py): a hold whose rows advance gen= on >= 90% of pairs is an animating
                 # single-buffered scene (the 1592-wide title: ~6 s, s7970 control 5.8 s at game t~44), not a freeze

def qrows(path):
    out = []
    try: data = subprocess.run(['zstd', '-dc', path], capture_output=True).stdout.decode('latin-1') if path.endswith('.zst') \
                else open(path, encoding='latin-1').read()
    except OSError: return out
    for l in data.split('\n')[:-1]:
        if l.startswith('Q ') and ' vi=' in l:
            p = l.split()
            try: out.append((float(p[1]), next(x[3:] for x in p if x.startswith('vi=')), next((x[4:] for x in p if x.startswith('gen=')), None)))
            except (ValueError, StopIteration): pass
    return out

def airows(path):
    out = []
    try:
        for l in open(path, encoding='latin-1'):
            p = l.split()
            if len(p) >= 3:
                try: out.append((float(p[0]), int(p[1])))
                except ValueError: pass
    except OSError: pass
    return out

def per_sec(ts, a, b):
    return [sum(1 for t in ts if a + i <= t < a + i + 1) for i in range(int(b - a))]

def score(Q, A, log, stop_s, at_s=None):
    r = {}
    if len(Q) < 100: return dict(verdict='noring', rows=len(Q))
    gi = max(range(len(Q) - 1), key=lambda i: Q[i + 1][0] - Q[i][0])
    if stop_s == 0 and at_s is not None:  # control arm: anchor at the same launch offset as the stop arms (ring opens ~3 s in)
        gi = min(range(len(Q) - 1), key=lambda i: abs(Q[i + 1][0] - (Q[0][0] + at_s - 3)))
    gap = Q[gi + 1][0] - Q[gi][0]; anc = Q[gi + 1][0]; pre = Q[gi][0]  # base = the 10 s before the last pre-stop row
    r['resume_gap_s'] = round(gap, 2)
    r['anchor_ok'] = int(abs(gap - stop_s) <= 3.0) if stop_s > 0 else 1
    tq = [q[0] for q in Q]
    sw = [Q[i][0] for i in range(1, len(Q)) if Q[i][1] != Q[i - 1][1]]
    bp, pp = per_sec(tq, pre - 10, pre), per_sec(tq, anc, anc + 30)
    bs, ps = per_sec(sw, pre - 10, pre), per_sec(sw, anc, anc + 30)
    r['base_pres'] = max(bp) if bp else 0; r['post_pres_max'] = max(pp) if pp else 0; r['post_pres_1s'] = pp[0] if pp else 0
    r['base_swaps'] = max(bs) if bs else 0; r['post_swaps_max'] = max(ps) if ps else 0
    # frozen VI after the anchor and max present gap after it
    post = [q for q in Q if anc <= q[0] <= anc + 30]
    hold = 0.0; mg = 0.0; anim = 0.0
    if post:
        s, v, _ = post[0]; G = []
        for t, x, g in post + [(post[-1][0], None, None)]:
            if x != v:
                adv = sum(1 for a, b in zip(G, G[1:]) if a != b)
                if len(G) > 1 and None not in G and adv / (len(G) - 1) >= ANIM_FRAC: anim = max(anim, t - s)
                else: hold = max(hold, t - s)
                s, v, G = t, x, []
            G.append(g)
        mg = max([b[0] - a[0] for a, b in zip(post, post[1:])] or [0])
    r['post_vihold_s'] = round(hold, 2); r['post_animhold_s'] = round(anim, 2); r['post_maxgap_ms'] = round(mg * 1e3, 1); r['post_rows'] = len(post)
    # AI: anchor on the AI trace's own largest gap (its own clock)
    if len(A) > 50:
        ai = max(range(len(A) - 1), key=lambda i: A[i + 1][0] - A[i][0]); aa, ap = A[ai + 1][0], A[ai][0]
        if stop_s == 0: aa = ap = A[0][0] + (anc - Q[0][0])
        ab, apb = per_sec([t for t, _ in A], ap - 10, ap), per_sec([t for t, _ in A], aa, aa + 30)
        r['ai_gap_s'] = round(A[ai + 1][0] - A[ai][0], 2)
        r['ai_base'] = max(ab) if ab else 0; r['ai_post_max'] = max(apb) if apb else 0
        r['ai_qmax_base'] = max([q for t, q in A if ap - 10 <= t < ap] or [0])
        r['ai_qmax_post'] = max([q for t, q in A if aa <= t < aa + 30] or [0])
        r['ai_zero_post'] = sum(1 for t, q in A if aa + 1 <= t < aa + 30 and q == 0)
    else:
        r['ai_rows'] = len(A)
    L = log.split('\n')
    r['reopen'] = sum(1 for l in L if '[s7199-hotplug] reopen' in l and 'why=resume' not in l)  # s7970: the fix's own reopen is expected
    r['reopen_resume'] = sum(1 for l in L if '[s7199-hotplug] reopen' in l and 'why=resume' in l)
    r['reopen_stall'] = sum(1 for l in L if '[s7199-hotplug] reopen' in l and 'why=stall' in l)
    r['crashlines'] = sum(1 for l in L if re.search(r'CRASH|SIGSEGV|SIGBUS|SIGABRT|terminate called|Assertion failed|abort\(', l))
    v = 'moot'
    if r['crashlines']: v = 'crash'
    elif not r['anchor_ok']: v = 'noanchor'
    elif r['post_pres_max'] > 1.5 * r['base_pres'] + 3 or r['post_swaps_max'] > 1.5 * r['base_swaps'] + 3 or \
         ('ai_post_max' in r and r['ai_post_max'] > 2 * r['ai_base'] + 3): v = 'burst'
    elif r['post_vihold_s'] > 5 or r['post_rows'] == 0 or r['post_maxgap_ms'] > 5000: v = 'stall'
    elif r['reopen']: v = 'reopen'
    r['verdict'] = v
    return r

def fmt(r): return ' '.join(f'{k}={v}' for k, v in r.items())

def selftest():
    def ring(stop, burst=0, freeze=0):
        Q = []; t = 100.0; k = 0
        g = 0
        for i in range(60 * 20): t += 1 / 60; k += (i % 2 == 0); g += 1; Q.append((t, f'{k:06X}', str(g)))
        t += stop
        for i in range(burst): t += 0.0005; g += 1; Q.append((t, f'{k + i:06X}', str(g)))
        k += burst
        for i in range(60 * 30):
            t += 1 / 60; held = i < abs(freeze) * 60; k += (i % 2 == 0) and not held; g += 1 if (not held or freeze < 0) else 0
            Q.append((t, f'{k:06X}', str(g)))
        return Q
    def ai(stop): return [(100 + i * 0.033, 4000) for i in range(600)] + [(100 + 600 * 0.033 + stop + i * 0.033, 4000) for i in range(900)]
    cases = [('moot', ring(60), 60, ''), ('burst', ring(60, burst=600), 60, ''), ('stall', ring(60, freeze=8), 60, ''), ('moot', ring(60, freeze=-7), 60, ''),
             ('reopen', ring(60), 60, '[s7199-hotplug] reopen n=1 why=drain-stall old=2 new=3'),
             ('moot', ring(60), 60, '[s7199-hotplug] reopen n=1 why=resume old=2 new=2'), ('noanchor', ring(10), 60, ''),
             ('moot', ring(0), 0, '')]
    ok = True
    for want, Q, s, lg in cases:
        got = score(Q, ai(s if want != 'noanchor' else 10), lg, s)['verdict']; ok &= got == want; print(f'selftest want={want} got={got}')
    print('SELFTEST', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 3)

def rescore(summ):
    """--rescore <dir>/<P>_summary.txt: keep each arm's runtime fields (alive, stop_ms, hup_exit_ms), re-run score() on its
    saved ring/AI/log (the e2e zstds the ring), rewrite the arm's score fields + PASS/FAIL and the VERDICT line."""
    import os
    d = os.path.dirname(summ); P = os.path.basename(summ)[:-len('_summary.txt')]; out = []; bad = 0
    for l in open(summ).read().split('\n'):
        m = re.match(rf'^{P} (\w+)_s(\d+): (alive_pre=\S+ alive=\S+ died_ms=\S+ status=\S+ stop_ms=\S+ hup_exit_ms=(\S+)) ', l)
        if m:
            sc, ln = m.group(1), int(m.group(2)); n = f'{d}/{P}_{sc}_s{ln}'; rg = n + '.ring.zst' if os.path.exists(n + '.ring.zst') else n + '.ring'
            try: lg = open(n + '.log', encoding='latin-1').read()
            except OSError: lg = ''
            r = score(qrows(rg), airows(n + '.ai'), lg, float(ln), 20.0 if sc == 'title' else 125.0)
            ok = 'alive_pre=alive alive=alive' in m.group(3) and m.group(4) not in ('hung', '-') and r['verdict'] == 'moot'
            bad |= not ok; out.append(f'{P} {sc}_s{ln}: {m.group(3)} {fmt(r)}'); out.append(f'{P} {sc}_s{ln} {"PASS" if ok else "FAIL"}'); continue
        if re.match(rf'^{P} \w+_s\d+ (PASS|FAIL)$', l): continue
        if l.startswith(f'{P} new_crash_reports='): bad |= not l.endswith('=0')
        if l.startswith(f'{P} VERDICT'): l = f'{P} VERDICT {"FAIL" if bad else "PASS"}'
        out.append(l)
    open(summ, 'w').write('\n'.join(out)); print(f'rescored {summ} bad={int(bad)}')

if __name__ == '__main__':
    if '--selftest' in sys.argv: selftest()
    if '--rescore' in sys.argv: rescore(sys.argv[sys.argv.index('--rescore') + 1]); sys.exit(0)
    ring, ai, logf, stop = sys.argv[1:5]; at = float(sys.argv[5]) if len(sys.argv) > 5 else None
    try: lg = open(logf, encoding='latin-1').read()
    except OSError: lg = ''
    print(fmt(score(qrows(ring), airows(ai), lg, float(stop), at)))
