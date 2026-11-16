#!/usr/bin/env python3
"""s7437 class CT analyzer: RT64 TMEMHasher::hash / XXH3 CPU per thread and per caller from /usr/bin/sample call trees.
Input: a tools/s7433_probe_cost.sh capture dir (sample_N.txt + samples.idx [+ run.tlog diag-quiet flips]), e.g. scratch/s7435.
Running SELF samples (wait leaves dropped) whose path contains a hash frame are classed:
  hasher  any frame on the path is RT64::TMEMHasher::hash; split into part = self (hash body incl. its unswizzle lambda)
          vs xxh (leaf is an XXH*/xxh function)
  xxh_other  an XXH* leaf with no TMEMHasher frame on the path (other RT64 hashers), charged to its first non-XXH caller
  ctrl    planted positive control rs64_diag_spin_us / rs64_store_diag_tick
The hasher caller = the frame directly above the outermost TMEMHasher::hash frame (who asks for the hash).
Share of one core = samples / thread-max samples per window; ms/frame = share * 1000 / fps.
CONTROL (unless --second-line): ctrl(busy=1) - ctrl(busy=0) >= 0.5 * busy_us * fps / 1e6.
VERDICT: H-small if hasher+xxh_other < 0.3 ms/frame; else H-candidate (step 2: repeat-fraction counter build).
usage: s7437_tmem_hash.py DIR [--busy-us 500] [--fps 60] [--second-line]  exit 0 = verdict, 3 = control fail"""
import re, sys, os, glob, argparse, collections, importlib.util
here = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('d'); ap.add_argument('--busy-us', type=float, default=500.0)
ap.add_argument('--fps', type=float, default=60.0); ap.add_argument('--second-line', action='store_true')
a = ap.parse_args()
LINE = re.compile(r'^([\s+!:|]*)(\d+) (.*)$')
WAIT = re.compile(r'mach_msg2_trap|__psynch_cvwait|semaphore_.*wait_trap|__semwait_signal|kevent|__select|'
                  r'__workq_kernreturn|mach_wait_until|__psynch_mutexwait|thread_suspend|poll$|__wait4|read$|__open|__ulock_wait')
CTRL = re.compile(r'^_?(rs64_store_diag_tick|rs64_diag_spin_us|rs64_diag_quiet_tick)')
HASH = re.compile(r'^RT64::TMEMHasher::hash'); XXH = re.compile(r'^(XXH|_?xxh)', re.I)
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
short = lambda s: re.sub(r'\(.*$', '', s)[:64]
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
K = ('hasher', 'h_self', 'h_xxh', 'xxh_other', 'ctrl')
agg = {0: collections.Counter(), 1: collections.Counter()}; nwin = {0: 0, 1: 0}; nw_all = 0
thr = collections.Counter(); caller = collections.Counter(); oth = collections.Counter(); tot = collections.Counter()
print('win start_s busy strad |   hasher   h_self    h_xxh xxh_other     ctrl  (share of one core)')
for fn in sorted(glob.glob(os.path.join(a.d, 'sample_*.txt')), key=lambda f: int(re.search(r'_(\d+)\.txt', f)[1])):
    i = int(re.search(r'_(\d+)\.txt', fn)[1]); st, w = idx.get(i, (0.0, 0.0))
    b0, b1 = busy_at(st + 0.5), busy_at(st + w + 1.5); strad = int(b0 != b1)
    c = collections.Counter(); th = collections.Counter(); ca = collections.Counter(); ot = collections.Counter(); nmax = 0
    for t in parse(fn):
        nmax = max(nmax, t['n']); tn = tname(t)
        for n in t['nodes']:
            sf = n['n'] - n['kids']
            if sf <= 0 or WAIT.search(n['s']): continue
            full = n['path'] + [n['s']]
            if any(CTRL.match(s) for s in full): c['ctrl'] += sf; continue
            hi = [k for k, s in enumerate(full) if HASH.match(s)]
            if hi:
                c['hasher'] += sf; c['h_xxh' if XXH.match(n['s']) else 'h_self'] += sf; th[tn] += sf
                ca[(tn, short(full[hi[0] - 1]) if hi[0] else '(root)')] += sf
            elif XXH.match(n['s']):
                c['xxh_other'] += sf
                up = [s for s in full if not XXH.match(s)]
                ot[(tn, short(up[-1]) if up else '(root)')] += sf
    if nmax == 0: continue
    print('%3d %7.1f %4d %5d | ' % (i, st, b0, strad) + ' '.join('%8.4f' % (c[k] / nmax) for k in K))
    nw_all += 1
    for k in K: tot[k] += c[k] / nmax
    for k, v in th.items(): thr[k] += v / nmax
    for k, v in ca.items(): caller[k] += v / nmax
    for k, v in ot.items(): oth[k] += v / nmax
    if not strad:
        nwin[b0] += 1
        for k in K: agg[b0][k] += c[k] / nmax
mf = lambda sh: sh * 1000.0 / a.fps
ok = True
if a.second_line: print('CONTROL SKIPPED (second-line capture, control passed in its own tool)')
elif not nwin[0] or not nwin[1]: print('VERDICT unevaluable: need busy-on and busy-off windows (%d/%d)' % (nwin[1], nwin[0])); sys.exit(3)
else:
    exp = a.busy_us * a.fps / 1e6; cd = agg[1]['ctrl'] / nwin[1] - agg[0]['ctrl'] / nwin[0]; ok = cd >= 0.5 * exp
    print('CONTROL ctrl delta %.4f core vs expected %.4f: %s' % (cd, exp, 'PASS' if ok else 'FAIL'))
print('mean over %d windows: ' % nw_all + ' '.join('%s=%.4f core (%.3f ms/f)' % (k, tot[k] / nw_all, mf(tot[k] / nw_all)) for k in K[:4]))
print('hasher per thread:')
for k, v in sorted(thr.items(), key=lambda kv: -kv[1])[:6]: print('  %-34s %.4f core  %.3f ms/frame' % (k[:34], v / nw_all, mf(v / nw_all)))
print('hasher callers (frame above outermost TMEMHasher::hash):')
for (tn, o), v in sorted(caller.items(), key=lambda kv: -kv[1])[:10]: print('  %-18s %-64s %.4f core %.3f ms/f' % (tn[:18], o, v / nw_all, mf(v / nw_all)))
print('other XXH callers:')
for (tn, o), v in sorted(oth.items(), key=lambda kv: -kv[1])[:8]: print('  %-18s %-64s %.4f core %.3f ms/f' % (tn[:18], o, v / nw_all, mf(v / nw_all)))
if not ok: print('VERDICT unevaluable: control FAIL'); sys.exit(3)
h = mf((tot['hasher'] + tot['xxh_other']) / nw_all)
print('VERDICT ' + ('H-small (hash total %.3f ms/frame < 0.3)' % h if h < 0.3 else 'H-candidate (hash total %.3f ms/frame >= 0.3: step 2 repeat-fraction counter)' % h))
