#!/usr/bin/env python3
"""s7435 class CR analyzer: host busy-wait / poll-loop CPU per site from /usr/bin/sample call trees.
Input: a tools/s7433_probe_cost.sh capture dir (sample_N.txt + samples.idx + run.tlog with [diag-quiet] flip lines).
Per window and per thread, running SELF samples are charged to one spin site (share of one core = self / thread samples):
  vi_spin   VI Thread, under vi_thread_func but not under sleep_until (the s6456 deadline tail spin, events.cpp)
  sem_spin  self in moodycamel LightweightSemaphore::wait*/waitWithPartialSpinning or wait_for_resumed (inlined spin,
            lightweightsemaphore.h maxSpins=10000)
  yield     swtch_pri / sched_yield / thread_switch leaves (std::this_thread::yield polls)
  clk_other clock leaves (mach_*_time, clock_gettime*) on any other path (timed polls elsewhere)
  ctrl      the planted positive control: rs64_diag_spin_us / rs64_store_diag_tick (ROGUESQ_DIAG_BUSY_GUEST_US per swap)
CONTROL: ctrl share (busy=1 windows) - ctrl share (busy=0 windows) >= 0.5 * busy_us * fps / 1e6 of one core.
VERDICT (NEXT s7435): H-tail if every live site < 0.05 core and total < 0.05; H-spin if one non-VI site >= 0.1 core;
H-sem if sem_spin is the largest non-VI term and >= 0.02 core; else H-tail-vi (VI deadline spin is the only >= 0.02 term).
usage: s7435_spin_cost.py DIR [--busy-us 500] [--fps 60]   exit 0 = verdict, 3 = control fail / unevaluable"""
import re, sys, os, glob, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from rs64_zopen import zopen  # s7724: retained sample_*.txt.zst
ap = argparse.ArgumentParser(); ap.add_argument('d'); ap.add_argument('--busy-us', type=float, default=500.0)
ap.add_argument('--fps', type=float, default=60.0); a = ap.parse_args()
LINE = re.compile(r'^([\s+!:|]*)(\d+) (.*)$')
WAIT = re.compile(r'mach_msg2_trap|__psynch_cvwait|semaphore_.*wait_trap|__ulock_wait|__semwait_signal|kevent|__select|'
                  r'__workq_kernreturn|mach_wait_until|__psynch_mutexwait|thread_suspend|poll$|__wait4|read$|__open')
YIELD = re.compile(r'^(swtch_pri|sched_yield|thread_switch)')
CLK = re.compile(r'^(mach_continuous_time|mach_absolute_time|clock_gettime|clock_gettime_nsec_np|DYLD-STUB\$\$clock_gettime|'
                 r'std::chrono::steady_clock::now|std::chrono::system_clock::now|mach_timebase_info)')
SEM = re.compile(r'^(moodycamel::LightweightSemaphore::wait|wait_for_resumed)')
CTRL = re.compile(r'^_?(rs64_store_diag_tick|rs64_diag_spin_us|rs64_diag_quiet_tick)')
def sym(t): return t.split('  (in ')[0].strip()
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
        node = {'dep': dep, 'n': cnt, 's': sym(txt), 'kids': 0, 'path': [x['s'] for x in stack]}
        if stack: stack[-1]['kids'] += cnt
        stack.append(node); cur['nodes'].append(node)
    return threads
def site(tname, path, leaf):
    full = path + [leaf]
    if any(CTRL.match(p) for p in full): return 'ctrl'
    if 'VI Thread' in tname and any(p.startswith('vi_thread_func') for p in path) and not any(p.startswith('ultramodern::sleep_until') for p in full):
        return 'vi_spin'
    if SEM.match(leaf): return 'sem_spin'
    if YIELD.match(leaf): return 'yield'
    if CLK.match(leaf):
        if any(SEM.match(p) for p in path): return 'sem_spin'
        return 'clk_other'
    return None
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
SITES = ('vi_spin', 'sem_spin', 'yield', 'clk_other', 'ctrl')
agg = {0: collections.Counter(), 1: collections.Counter()}; nwin = {0: 0, 1: 0}
perthr = collections.Counter()
print('win start_s busy straddle | ' + ' '.join('%9s' % s for s in SITES) + '  (share of one core)')
for fn in sorted((glob.glob(os.path.join(a.d, 'sample_*.txt')) or glob.glob(os.path.join(a.d, 'sample_*.txt.zst'))), key=lambda f: int(re.search(r'_(\d+)\.txt', f)[1])):
    i = int(re.search(r'_(\d+)\.txt', fn)[1]); st, w = idx.get(i, (0.0, 0.0))
    b0, b1 = busy_at(st + 0.5), busy_at(st + w + 1.5); strad = int(b0 != b1)
    c = collections.Counter(); nmax = 0
    for t in parse(fn):
        nmax = max(nmax, t['n'])
        for n in t['nodes']:
            sf = n['n'] - n['kids']
            if sf <= 0 or WAIT.search(n['s']): continue
            s = site(t['name'], n['path'], n['s'])
            if s: c[s] += sf; perthr[(s, re.sub(r'^Thread_\d+:?\s*', '', t['name']) or '(unnamed)')] += sf if not strad else 0
    if nmax == 0: continue
    sh = {s: c[s] / nmax for s in SITES}
    print('%3d %7.1f %4d %8d | ' % (i, st, b0, strad) + ' '.join('%9.4f' % sh[s] for s in SITES))
    if not strad:
        nwin[b0] += 1
        for s in SITES: agg[b0][s] += sh[s]
if not nwin[0] or not nwin[1]: print('VERDICT unevaluable: need busy-on and busy-off windows (%d/%d)' % (nwin[1], nwin[0])); sys.exit(3)
m = {b: {s: agg[b][s] / nwin[b] for s in SITES} for b in (0, 1)}
exp = a.busy_us * a.fps / 1e6; cd = m[1]['ctrl'] - m[0]['ctrl']
ok = cd >= 0.5 * exp
print('busy=0 mean: ' + ' '.join('%s=%.4f' % (s, m[0][s]) for s in SITES))
print('busy=1 mean: ' + ' '.join('%s=%.4f' % (s, m[1][s]) for s in SITES))
print('CONTROL ctrl delta %.4f core vs expected %.4f (busy_us*fps): %s' % (cd, exp, 'PASS' if ok else 'FAIL'))
tot_s = 0
nb0 = sum(1 for _ in range(nwin[0])) or 1
print('per-thread self samples (all non-straddle windows):')
for (s, th), v in sorted(perthr.items(), key=lambda kv: -kv[1])[:14]:
    if s != 'ctrl': print('  %-9s %-32s %6d' % (s, th[:32], v))
if not ok: print('VERDICT unevaluable: control FAIL'); sys.exit(3)
z = m[0]; live = {s: z[s] for s in SITES if s != 'ctrl'}; total = sum(live.values())
nonvi = {s: v for s, v in live.items() if s != 'vi_spin'}
top = max(nonvi, key=nonvi.get)
if max(nonvi.values()) >= 0.1: v = 'H-spin (%s %.3f core)' % (top, nonvi[top])
elif top == 'sem_spin' and nonvi[top] >= 0.02: v = 'H-sem (sem_spin %.3f core)' % nonvi[top]
elif total < 0.05: v = 'H-tail (total %.3f core)' % total
else: v = 'H-tail-vi (vi_spin %.3f core, non-VI %.3f; total %.3f)' % (live['vi_spin'], sum(nonvi.values()), total)
print('VERDICT ' + v)
