#!/usr/bin/env python3
"""s7441 class CX census: every rs64-named frame (rs64_*, rs64X*, Rs64*, (anonymous namespace)::rs64*) in a
tools/s7433_probe_cost.sh capture, on EVERY thread, by self and inclusive ms/frame (same normalisation as
s7438_rt64_terms.py: samples / thread-max per window, * 1000 / fps / windows). Each symbol is mapped to the lib/rt64 or src
file that defines it (grep), so the per-draw/per-frame hooks of a file set can be ranked without reading every call site.
usage: s7441_rs64_census.py DIR [--fps 60] [--min 0.005] [--files a.cpp,b.cpp]   (exit 0)"""
import re, sys, os, glob, argparse, collections, subprocess
ap = argparse.ArgumentParser(); ap.add_argument('d'); ap.add_argument('--fps', type=float, default=60.0)
ap.add_argument('--min', type=float, default=0.005); ap.add_argument('--files', default='')
a = ap.parse_args()
LINE = re.compile(r'^([\s+!:|]*)(\d+) (.*)$')
WAIT = re.compile(r'mach_msg2_trap|__psynch_cvwait|semaphore_.*wait_trap|__semwait_signal|kevent|__select|'
                  r'__workq_kernreturn|mach_wait_until|__psynch_mutexwait|thread_suspend|poll$|__wait4|read$|__open|__ulock_wait')
RS = re.compile(r'^(?:\(anonymous namespace\)::|[A-Za-z0-9_]+::)*_?([Rr]s64[A-Za-z0-9_]*)')
def sym(t):
    m = re.match(r'^(.*?)\s+\(in ([^)]*)\)', t); s = (m[1] if m else t).strip()
    r = RS.match(s); return r[1] if r else None
nwin = 0; selfc = collections.Counter(); incl = collections.Counter(); thr = collections.defaultdict(set)
for fn in glob.glob(os.path.join(a.d, 'sample_*.txt')):
    stack = []; sc = collections.Counter(); ic = collections.Counter(); nmax = 0; tn = ''
    nodes = []
    for raw in open(fn, errors='replace'):
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
mf = lambda v: v * 1000.0 / a.fps / max(nwin, 1)
def where(s):
    r = subprocess.run(['grep', '-rlE', r'(^|[ *&:])' + s + r'\s*\(', 'lib/rt64/src', 'src', 'lib/N64ModernRuntime/librecomp/src',
                        '--include=*.cpp', '--include=*.c', '--include=*.h'], capture_output=True, text=True).stdout.split()
    return ','.join(sorted(set(os.path.basename(x) for x in r)))[:60] or '?'
want = set(x.strip() for x in a.files.split(',') if x.strip())
print('windows=%d  (ms/frame; self = innermost rs64 frame has the sample)' % nwin)
print('%-40s %8s %8s  %-60s %s' % ('symbol', 'self', 'incl', 'defined-in', 'threads'))
rows = sorted(incl, key=lambda k: -incl[k])
for k in rows:
    if mf(incl[k]) < a.min and mf(selfc[k]) < a.min: continue
    w = where(k)
    if want and not (set(w.split(',')) & want): continue
    print('%-40s %8.3f %8.3f  %-60s %s' % (k[:40], mf(selfc[k]), mf(incl[k]), w, ','.join(sorted(thr[k]))[:40]))
