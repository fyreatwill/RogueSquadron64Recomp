#!/usr/bin/env python3
"""s7438 class CU analyzer: rank every RT64 (RT64:: / rs64*) frame on the Gfx thread (and other RT64 threads) by
self and inclusive CPU from /usr/bin/sample call trees, so each term can be checked against its prior closure.
Input: a tools/s7433_probe_cost.sh capture dir (sample_N.txt + samples.idx [+ run.tlog diag-quiet flips]), e.g. scratch/s7435.
Running SELF samples (wait leaves dropped) are charged to the INNERMOST RT64 frame on their path (self table), and to every
distinct RT64 frame on their path (inclusive table). Non-RT64 innermost paths on the Gfx thread go to '(ours/other)'.
Share of one core = samples / thread-max samples per window; ms/frame = share * 1000 / fps.
CONTROL (unless --second-line): planted rs64_diag_spin_us ctrl(busy=1) - ctrl(busy=0) >= 0.5 * busy_us * fps / 1e6.
VERDICT: H-diffuse if no RT64 self term >= 0.2 ms/f; else list terms >= 0.2 for prior-closure check (H-closed / H-new).
usage: s7438_rt64_terms.py DIR [--busy-us 500] [--fps 60] [--second-line] [--top 20] [--under RT64::GBI_RDP::decodeTriangles]  exit 0 = verdict, 3 = control fail"""
import re, sys, os, glob, argparse, collections
ap = argparse.ArgumentParser(); ap.add_argument('d'); ap.add_argument('--busy-us', type=float, default=500.0)
ap.add_argument('--fps', type=float, default=60.0); ap.add_argument('--second-line', action='store_true')
ap.add_argument('--top', type=int, default=20)
ap.add_argument('--under', default='', help='also break down Gfx-thread self samples below the innermost frame with this prefix')
a = ap.parse_args()
LINE = re.compile(r'^([\s+!:|]*)(\d+) (.*)$')
WAIT = re.compile(r'mach_msg2_trap|__psynch_cvwait|semaphore_.*wait_trap|__semwait_signal|kevent|__select|'
                  r'__workq_kernreturn|mach_wait_until|__psynch_mutexwait|thread_suspend|poll$|__wait4|read$|__open|__ulock_wait')
CTRL = re.compile(r'^_?(rs64_store_diag_tick|rs64_diag_spin_us|rs64_diag_quiet_tick)')
RT = re.compile(r'^(RT64::|_?rs64[A-Z])')
RTTHR = re.compile(r'Gfx Thread|RT64')
def split(t):
    m = re.match(r'^(.*?)\s+\(in ([^)]*)\)', t)
    return (m[1].strip(), m[2]) if m else (t.strip(), '')
def parse(fn):
    threads = []; stack = []; cur = None
    for raw in open(fn, errors='replace'):
        if raw.startswith('Total number in stack') or raw.startswith('Sort by top'): break
        m = LINE.match(raw.rstrip('\n'))
        if not m: continue
        dep, cnt, txt = len(m[1]), int(m[2]), m[3]
        if txt.startswith('Thread_') and (cur is None or dep <= cur['dep']):
            cur = {'name': txt.strip(), 'dep': dep, 'n': cnt, 'nodes': []}; threads.append(cur); stack = []; continue
        if cur is None: continue
        while stack and stack[-1]['dep'] >= dep: stack.pop()
        s, lib = split(txt)
        node = {'dep': dep, 'n': cnt, 's': s, 'lib': lib, 'kids': 0, 'path': [x['s'] for x in stack]}
        if stack: stack[-1]['kids'] += cnt
        stack.append(node); cur['nodes'].append(node)
    return threads
def tname(t):
    n = re.sub(r'^Thread_\d+:?\s*', '', t['name']); n = re.sub(r'DispatchQueue_\d+: ', '', n)
    return n.split('  ')[0].strip() or '(unnamed)'
def short(s):
    s = re.sub(r'\(.*$', '', s); s = re.sub(r'<.*>', '<>', s); return s[:70]
flips = []
tl = os.path.join(a.d, 'run.tlog')
for l in open(tl, errors='replace') if os.path.exists(tl) else []:
    m = re.search(r'\[diag-quiet\] flip quiet=(\d) busy=(\d) t=([\d.]+)', l)
    if m: flips.append((float(m[3]), int(m[2])))
def busy_at(t):
    b = 0
    for ft, fb in flips:
        if ft <= t: b = fb
    return b
idx = {}
for l in open(os.path.join(a.d, 'samples.idx')):
    i, st, w = l.split(); idx[int(i)] = (float(st), float(w))
under = collections.Counter(); selfc = collections.Counter(); incl = collections.Counter(); thrtot = collections.Counter()
ctrl = {0: 0.0, 1: 0.0}; nwin = {0: 0, 1: 0}; nw_all = 0
for fn in sorted(glob.glob(os.path.join(a.d, 'sample_*.txt')), key=lambda f: int(re.search(r'_(\d+)\.txt', f)[1])):
    i = int(re.search(r'_(\d+)\.txt', fn)[1]); st, w = idx.get(i, (0.0, 0.0))
    b0, b1 = busy_at(st + 0.5), busy_at(st + w + 1.5); strad = int(b0 != b1)
    uc = collections.Counter(); sc = collections.Counter(); ic = collections.Counter(); tt = collections.Counter(); cc = 0; nmax = 0
    for t in parse(fn):
        nmax = max(nmax, t['n']); tn = tname(t); rtt = bool(RTTHR.search(tn))
        for n in t['nodes']:
            sf = n['n'] - n['kids']
            if sf <= 0 or WAIT.search(n['s']): continue
            full = n['path'] + [n['s']]
            if any(CTRL.match(s) for s in full): cc += sf; continue
            if not rtt: continue
            tk = 'Gfx' if 'Gfx' in tn else tn
            tt[tk] += sf
            rts = [short(s) for s in full if RT.match(s)]
            sc[(tk, rts[-1] if rts else '(non-RT64 path)')] += sf
            for f in set(rts): ic[(tk, f)] += sf
            if a.under and tk == 'Gfx':
                ku = [j for j, s in enumerate(full) if s.startswith(a.under)]
                if ku: b = full[ku[-1] + 1:]; uc[short(b[0]) if b else '(self)'] += sf
    if nmax == 0: continue
    nw_all += 1
    for k, v in sc.items(): selfc[k] += v / nmax
    for k, v in ic.items(): incl[k] += v / nmax
    for k, v in tt.items(): thrtot[k] += v / nmax
    for k, v in uc.items(): under[k] += v / nmax
    if not strad: nwin[b0] += 1; ctrl[b0] += cc / nmax
mf = lambda sh: sh * 1000.0 / a.fps / nw_all
ok = True
if a.second_line: print('CONTROL SKIPPED (second-line capture)')
elif not nwin[0] or not nwin[1]: print('VERDICT unevaluable: need busy-on and busy-off windows (%d/%d)' % (nwin[1], nwin[0])); sys.exit(3)
else:
    exp = a.busy_us * a.fps / 1e6; cd = ctrl[1] / nwin[1] - ctrl[0] / nwin[0]; ok = cd >= 0.5 * exp
    print('CONTROL ctrl delta %.4f core vs expected %.4f: %s' % (cd, exp, 'PASS' if ok else 'FAIL'))
print('windows=%d  running ms/frame per thread:' % nw_all, ', '.join('%s=%.2f' % (k[:16], mf(v)) for k, v in sorted(thrtot.items(), key=lambda kv: -kv[1])[:8]))
print('SELF (innermost RT64 frame), top %d:' % a.top)
for (tk, f), v in sorted(selfc.items(), key=lambda kv: -kv[1])[:a.top]: print('  %-12s %-70s %.3f ms/f' % (tk[:12], f, mf(v)))
print('INCLUSIVE (Gfx thread), top %d:' % a.top)
for (tk, f), v in sorted([kv for kv in incl.items() if kv[0][0] == 'Gfx'], key=lambda kv: -kv[1])[:a.top]: print('  %-70s %.3f ms/f' % (f, mf(v)))
if a.under:
    print('UNDER %s (Gfx, first frame below it):' % a.under)
    for f, v in sorted(under.items(), key=lambda kv: -kv[1])[:a.top]: print('  %-70s %.3f ms/f' % (f, mf(v)))
if not ok: print('VERDICT unevaluable: control FAIL'); sys.exit(3)
big = [(k, mf(v)) for k, v in selfc.items() if mf(v) >= 0.2 and k[1] != '(non-RT64 path)']
print('VERDICT ' + ('H-diffuse (no RT64 self term >= 0.2 ms/f)' if not big else 'terms >= 0.2 ms/f for prior-closure check: ' + '; '.join('%s %s %.3f' % (k[0], k[1], v) for k, v in sorted(big, key=lambda x: -x[1]))))
