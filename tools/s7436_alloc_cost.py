#!/usr/bin/env python3
"""s7436 class CS analyzer: host heap-allocator CPU per thread and per owned caller from /usr/bin/sample call trees.
Input: a tools/s7433_probe_cost.sh capture dir (sample_N.txt + samples.idx + run.tlog [diag-quiet] flip lines), e.g. scratch/s7435.
Running SELF samples (wait leaves dropped) are classed:
  alloc  leaf in libsystem_malloc, or operator new/delete, or any frame on the path in libsystem_malloc (lock/kernel
         leaves beneath malloc count here too and are ALSO tallied as 'lock' when the leaf is an unfair-lock/ulock wait)
  ctrl   planted positive control rs64_diag_spin_us / rs64_store_diag_tick (ROGUESQ_DIAG_BUSY_GUEST_US per swap)
Each alloc sample is charged to its innermost OWNED caller: the deepest frame in the RogueSquadron64Recomp image whose
symbol is not a std::/__1:: template (vector growth -> its owner), else the deepest non-malloc library frame.
Share of one core = samples / thread-max samples per window. ms/frame = share * 1000 / fps.
CONTROL: ctrl(busy=1) - ctrl(busy=0) >= 0.5 * busy_us * fps / 1e6.
VERDICT: H-lock if lock-under-malloc >= 0.01 core; H-hot if one owned caller on Gfx/MAIN >= 0.01 core; H-free if
allocator total < 0.02 core; else H-diffuse (total >= 0.02, no single caller >= 0.01).
usage: s7436_alloc_cost.py DIR [--busy-us 500] [--fps 60]   exit 0 = verdict, 3 = control fail / unevaluable"""
import re, sys, os, glob, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from rs64_zopen import zopen  # s7724: retained sample_*.txt.zst
ap = argparse.ArgumentParser(); ap.add_argument('d'); ap.add_argument('--busy-us', type=float, default=500.0)
ap.add_argument('--fps', type=float, default=60.0)
ap.add_argument('--second-line', action='store_true', help='busy-off-only capture whose control passed in its own tool: report shares, skip CONTROL')
a = ap.parse_args()
LINE = re.compile(r'^([\s+!:|]*)(\d+) (.*)$')
WAIT = re.compile(r'mach_msg2_trap|__psynch_cvwait|semaphore_.*wait_trap|__semwait_signal|kevent|__select|'
                  r'__workq_kernreturn|mach_wait_until|__psynch_mutexwait|thread_suspend|poll$|__wait4|read$|__open')
LOCK = re.compile(r'^(__ulock_wait2?|_os_unfair_lock_lock_slow|__psynch_mutexwait)')
CTRL = re.compile(r'^_?(rs64_store_diag_tick|rs64_diag_spin_us|rs64_diag_quiet_tick)')
NEWDEL = re.compile(r'^operator (new|delete)')
def split(t):
    m = re.match(r'^(.*?)\s+\(in ([^)]*)\)', t)
    return (m[1].strip(), m[2]) if m else (t.strip(), '')
def parse(fn):
    threads = []; stack = []; cur = None
    for raw in zopen(fn, errors='replace'):
        if raw.startswith('Total number in stack') or raw.startswith('Sort by top'): break
        m = LINE.match(raw.rstrip('\n'))
        if not m: continue
        dep, cnt, txt = len(m[1]), int(m[2]), m[3]
        if txt.startswith('Thread_') and (cur is None or dep <= cur['dep']):
            cur = {'name': txt.strip(), 'dep': dep, 'n': cnt, 'nodes': []}; threads.append(cur); stack = []; continue
        if cur is None: continue
        while stack and stack[-1]['dep'] >= dep: stack.pop()
        s, lib = split(txt)
        node = {'dep': dep, 'n': cnt, 's': s, 'lib': lib, 'kids': 0, 'path': [(x['s'], x['lib']) for x in stack]}
        if stack: stack[-1]['kids'] += cnt
        stack.append(node); cur['nodes'].append(node)
    return threads
def is_alloc(fr): s, lib = fr; return lib == 'libsystem_malloc.dylib' or bool(NEWDEL.match(s))
def owner(path):
    for s, lib in reversed(path):
        if lib == 'RogueSquadron64Recomp' and not re.match(r'^(std::|__1::|void std::|\w+\* std::)', s) and not is_alloc((s, lib)):
            return re.sub(r'\(.*$', '', s)[:60]
    for s, lib in reversed(path):
        if not is_alloc((s, lib)): return (re.sub(r'\(.*$', '', s)[:44] + ' [' + lib[:14] + ']')
    return '(root)'
def tname(t):
    n = re.sub(r'^Thread_\d+:?\s*', '', t['name']); n = re.sub(r'DispatchQueue_\d+: ', '', n)
    return n.split('  ')[0].strip() or '(unnamed)'
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
agg = {0: collections.Counter(), 1: collections.Counter()}; nwin = {0: 0, 1: 0}
thr_sh = collections.Counter(); own_sh = collections.Counter(); leaf_sh = collections.Counter(); nw_all = 0
print('win start_s busy strad |    alloc     lock     ctrl  (share of one core)')
for fn in sorted((glob.glob(os.path.join(a.d, 'sample_*.txt')) or glob.glob(os.path.join(a.d, 'sample_*.txt.zst'))), key=lambda f: int(re.search(r'_(\d+)\.txt', f)[1])):
    i = int(re.search(r'_(\d+)\.txt', fn)[1]); st, w = idx.get(i, (0.0, 0.0))
    b0, b1 = busy_at(st + 0.5), busy_at(st + w + 1.5); strad = int(b0 != b1)
    c = collections.Counter(); th = collections.Counter(); ow = collections.Counter(); lf = collections.Counter(); nmax = 0
    for t in parse(fn):
        nmax = max(nmax, t['n']); tn = tname(t)
        for n in t['nodes']:
            sf = n['n'] - n['kids']
            if sf <= 0: continue
            full = n['path'] + [(n['s'], n['lib'])]
            if any(CTRL.match(s) for s, _ in full): c['ctrl'] += sf; continue
            if not any(is_alloc(fr) for fr in full): continue
            if LOCK.match(n['s']): c['lock'] += sf
            elif WAIT.search(n['s']): continue
            c['alloc'] += sf; th[tn] += sf; ow[(tn, owner(n['path'] if is_alloc((n['s'], n['lib'])) else n['path']))] += sf
            lf[n['s']] += sf
    if nmax == 0: continue
    print('%3d %7.1f %4d %5d | %8.4f %8.4f %8.4f' % (i, st, b0, strad, c['alloc'] / nmax, c['lock'] / nmax, c['ctrl'] / nmax))
    nw_all += 1
    for k, v in th.items(): thr_sh[k] += v / nmax
    for k, v in ow.items(): own_sh[k] += v / nmax
    for k, v in lf.items(): leaf_sh[k] += v / nmax
    if not strad:
        nwin[b0] += 1
        for s in ('alloc', 'lock', 'ctrl'): agg[b0][s] += c[s] / nmax
if a.second_line and nwin[0]:
    nwin[1] = 1
elif not nwin[0] or not nwin[1]: print('VERDICT unevaluable: need busy-on and busy-off windows (%d/%d)' % (nwin[1], nwin[0])); sys.exit(3)
m = {b: {s: agg[b][s] / nwin[b] for s in ('alloc', 'lock', 'ctrl')} for b in (0, 1)}
exp = a.busy_us * a.fps / 1e6; cd = m[1]['ctrl'] - m[0]['ctrl']; ok = cd >= 0.5 * exp or a.second_line
for b in (0, 1): print('busy=%d mean (%d win): ' % (b, nwin[b]) + ' '.join('%s=%.4f' % (s, m[b][s]) for s in ('alloc', 'lock', 'ctrl')))
print('CONTROL ctrl delta %.4f core vs expected %.4f: %s' % (cd, exp, 'SKIPPED (second-line capture)' if a.second_line else ('PASS' if ok else 'FAIL')))
mf = lambda sh: sh * 1000.0 / a.fps
print('per-thread allocator share (mean over %d windows):' % nw_all)
for k, v in sorted(thr_sh.items(), key=lambda kv: -kv[1])[:10]: print('  %-34s %.4f core  %.3f ms/frame' % (k[:34], v / nw_all, mf(v / nw_all)))
print('top owned callers:')
for (tn, o), v in sorted(own_sh.items(), key=lambda kv: -kv[1])[:16]: print('  %-20s %-60s %.4f core %.3f ms/f' % (tn[:20], o, v / nw_all, mf(v / nw_all)))
print('top allocator leaves:')
for k, v in sorted(leaf_sh.items(), key=lambda kv: -kv[1])[:8]: print('  %-48s %.4f core' % (k[:48], v / nw_all))
if not ok: print('VERDICT unevaluable: control FAIL'); sys.exit(3)
tot = sum(thr_sh.values()) / nw_all; lock = (m[0]['lock'] + m[1]['lock']) / 2
hot = [(k, v / nw_all) for k, v in own_sh.items() if re.search(r'Gfx|MAIN|main|Game|guest', k[0], re.I) and v / nw_all >= 0.01]
if lock >= 0.01: v = 'H-lock (lock-under-malloc %.4f core)' % lock
elif hot: k, x = max(hot, key=lambda kv: kv[1]); v = 'H-hot (%s / %s %.4f core)' % (k[0], k[1], x)
elif tot < 0.02: v = 'H-free (allocator total %.4f core, %.3f ms/frame; lock %.4f)' % (tot, mf(tot), lock)
else: v = 'H-diffuse (allocator total %.4f core, no caller >= 0.01)' % tot
print('VERDICT ' + v)
