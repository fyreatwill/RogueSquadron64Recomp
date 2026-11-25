#!/usr/bin/env python3
"""s7441 class CX census: every rs64-named frame (rs64_*, rs64X*, Rs64*, (anonymous namespace)::rs64*) in a
tools/s7433_probe_cost.sh capture, on EVERY thread, by self and inclusive ms/frame (same normalisation as
s7438_rt64_terms.py: samples / thread-max per window, * 1000 / fps / windows). Each symbol is mapped to the lib/rt64 or src
file that defines it (grep), so the per-draw/per-frame hooks of a file set can be ranked without reading every call site.
usage: s7441_rs64_census.py DIR [--fps 60] [--min 0.005] [--files a.cpp,b.cpp]   (exit 0)
       s7441_rs64_census.py DIR --gate [--control PRE_DIR] [--windows 8]
s7803 gate (the ledger's s7441 claims over a retained capture): windows == --windows; rs64SkipDraw inclusive < 0.003 ms/f
(the s7441 load-time latch; pre-fix s7439 0.007); no rs64 frame >= 0.003 ms/f defined in the s7441 named file set. --control
runs the same check on a pre-fix capture, which must read FAIL (planted RED, same run). Exit 0 iff gate PASS and control FAILs.
s7935: --plant builds two planted REDs from DIR itself (s7439 was pruned): rs64LoadBlockRuns->rs64SkipDraw and rs64_spike_scan->
rs64_s7463_hash (reviewed post-s7441 hook, REVIEWED budget 0.02 ms/f incl). Live capture: scratch/s7935 (fresh owner-recipe run).
Since s7803 sample_N.txt.zst is read too (the raw-only glob read windows=0 on every retained capture)."""
import re, sys, os, glob, argparse, collections, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rs64_zopen import zopen  # s7803: samples are retained as sample_N.txt.zst since 2026-11-16
ap = argparse.ArgumentParser(); ap.add_argument('d'); ap.add_argument('--fps', type=float, default=60.0)
ap.add_argument('--min', type=float, default=0.005); ap.add_argument('--files', default='')
ap.add_argument('--gate', action='store_true'); ap.add_argument('--control')
ap.add_argument('--plant', action='store_true', help='s7935: planted controls built from DIR itself (pre-fix s7439 capture was pruned)'); ap.add_argument('--windows', type=int, default=8)
a = ap.parse_args()
LINE = re.compile(r'^([\s+!:|]*)(\d+) (.*)$')
WAIT = re.compile(r'mach_msg2_trap|__psynch_cvwait|semaphore_.*wait_trap|__semwait_signal|kevent|__select|'
                  r'__workq_kernreturn|mach_wait_until|__psynch_mutexwait|thread_suspend|poll$|__wait4|read$|__open|__ulock_wait')
RS = re.compile(r'^(?:\(anonymous namespace\)::|[A-Za-z0-9_]+::)*_?([Rr]s64[A-Za-z0-9_]*)')
def sym(t):
    m = re.match(r'^(.*?)\s+\(in ([^)]*)\)', t); s = (m[1] if m else t).strip()
    r = RS.match(s); return r[1] if r else None
def samples(d):  # s7803: one file per window, plain or .zst (the raw-only glob read 0 windows once they were compressed)
    got = {}
    for f in glob.glob(os.path.join(d, 'sample_*.txt')) + glob.glob(os.path.join(d, 'sample_*.txt.zst')):
        got.setdefault(re.sub(r'\.zst$', '', os.path.basename(f)), f)
    return [got[k] for k in sorted(got)]
def census(d):
    nwin = 0; selfc = collections.Counter(); incl = collections.Counter(); thr = collections.defaultdict(set)
    for fn in samples(d):
        stack = []; sc = collections.Counter(); ic = collections.Counter(); nmax = 0; tn = ''
        nodes = []
        for raw in zopen(fn):
            if raw.startswith('Total number in stack'): break
            m = LINE.match(raw.rstrip('\n'))
            if not m: continue
            dep, cnt, txt = len(m[1]), int(m[2]), m[3]
            if txt.startswith('Thread_'):
                for n in nodes: pass
                stack = []; tn = re.sub(r'^Thread_\d+:?\s*', '', txt).split('  ')[0]; nmax = max(nmax, cnt); continue
            while stack and stack[-1]['dep'] >= dep: stack.pop()
            node = {'dep': dep, 'n': cnt, 'kids': 0, 'r': sym(txt), 'tn': tn,
                    'path': [x['r'] for x in stack if x['r']], 'wait': bool(WAIT.search(txt))}
            if stack: stack[-1]['kids'] += cnt
            stack.append(node); nodes.append(node)
        for n in nodes:
            sf = n['n'] - n['kids']
            if sf <= 0 or n['wait']: continue
            full = n['path'] + ([n['r']] if n['r'] else [])
            if not full: continue
            if n['r']: sc[n['r']] += sf
            for f in set(full): ic[f] += sf; thr[f].add(n['tn'][:20])
        if not nmax: continue
        nwin += 1
        for k, v in sc.items(): selfc[k] += v / nmax
        for k, v in ic.items(): incl[k] += v / nmax
    return nwin, selfc, incl, thr
nwin, selfc, incl, thr = census(a.d)
mf = lambda v, n=None: v * 1000.0 / a.fps / max(nwin if n is None else n, 1)
def where(s):
    r = subprocess.run(['grep', '-rlE', r'(^|[ *&:])' + s + r'\s*\(', 'lib/rt64/src', 'src', 'lib/N64ModernRuntime/librecomp/src',
                        '--include=*.cpp', '--include=*.c', '--include=*.h'], capture_output=True, text=True).stdout.split()
    return ','.join(sorted(set(os.path.basename(x) for x in r)))[:60] or '?'
# s7935: hooks added to the named file set AFTER s7441, reviewed, each with an inclusive ms/f budget. rs64_s7463_hash is the
# s7463 padding-zeroed XXH3 wrapper (ROGUESQ_S7463_PADFIX; default-on correctness fix): its inclusive time is mostly the XXH3
# call RT64 made directly before s7463 (s7935 capture: self 0.004, incl 0.012 ms/f). Over budget still reads FAIL.
REVIEWED = {'rs64_s7463_hash': 0.02}
NAMED = ('rt64_framebuffer_renderer.cpp', 'rt64_state.cpp', 'rt64_present_queue.cpp', 'rt64_rdp_tmem.cpp', 'rt64_workload_queue.cpp')
def gate(tag, d, cen):
    n, sc, ic, _ = cen
    skip = mf(ic.get('rs64SkipDraw', 0), n)
    named = sorted(((mf(max(ic[k], sc[k]), n), k, w) for k in ic if mf(max(ic[k], sc[k]), n) >= 0.003
                    if mf(ic[k], n) >= REVIEWED.get(k, 0)
                    for w in [where(k)] if any(f in NAMED or (f.startswith('rt64_framebuffer') and f.endswith('.cpp')) for f in w.split(','))),
                   reverse=True)
    bad = []
    if n != a.windows: bad.append('windows=%d!=%d' % (n, a.windows))
    if skip >= 0.003: bad.append('rs64SkipDraw=%.3f>=0.003' % skip)
    if named: bad.append('named=' + ','.join('%s:%.3f' % (k, v) for v, k, w in named[:4]))
    print('%s dir=%s windows=%d rs64SkipDraw_incl=%.4f named_ge_0.003=%d -> %s%s' % (
        tag, d, n, skip, len(named), 'FAIL' if bad else 'PASS', (' (' + '; '.join(bad) + ')') if bad else ''))
    return not bad
if a.gate:
    ok = gate('GATE', a.d, (nwin, selfc, incl, thr))
    cok = True
    if a.control:
        cfail = not gate('CONTROL', a.control, census(a.control))
        print('CONTROL %s (pre-fix capture must read FAIL)' % ('PASS' if cfail else 'FAIL'))
        cok = cfail
    if a.plant:  # s7935: (1) a hot Gfx frame renamed rs64SkipDraw, (2) one renamed into the reviewed hook past its budget
        import tempfile
        for lbl, src, dst in (('skipdraw', 'rs64LoadBlockRuns', 'rs64SkipDraw'), ('reviewed', 'rs64_spike_scan', 'rs64_s7463_hash')):
            with tempfile.TemporaryDirectory() as td:
                hit = 0
                for i, fn in enumerate(samples(a.d)):
                    t = ''.join(zopen(fn)); hit += t.count(src)
                    open(os.path.join(td, 'sample_%d.txt' % (i + 1)), 'w').write(t.replace(src, dst))
                pf = hit > 0 and not gate('PLANT-' + lbl, td, census(td))
                print('PLANT %s %s->%s hits=%d %s' % (lbl, src, dst, hit, 'PASS' if pf else 'FAIL'))
                cok = cok and pf
    print('VERDICT %s' % ('GREEN' if ok and cok else 'RED'))
    sys.exit(0 if ok and cok else 1)
want = set(x.strip() for x in a.files.split(',') if x.strip())
print('windows=%d  (ms/frame; self = innermost rs64 frame has the sample)' % nwin)
print('%-40s %8s %8s  %-60s %s' % ('symbol', 'self', 'incl', 'defined-in', 'threads'))
rows = sorted(incl, key=lambda k: -incl[k])
for k in rows:
    if mf(incl[k]) < a.min and mf(selfc[k]) < a.min: continue
    w = where(k)
    if want and not (set(w.split(',')) & want): continue
    print('%-40s %8.3f %8.3f  %-60s %s' % (k[:40], mf(selfc[k]), mf(incl[k]), w, ','.join(sorted(thr[k]))[:40]))
