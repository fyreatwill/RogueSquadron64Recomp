#!/usr/bin/env python3
"""s7433 class CP analyzer: guest-thread CPU attribution from /usr/bin/sample call trees (external profiler).
Input dir: run.tlog (ms-stamped, [diag-quiet] flip lines), samples.idx (i start_s W), sample_<i>.txt.
Guest threads = host threads named '[Game] <N64 thread>'. Per window: running samples (self samples not at a wait leaf),
probe samples = running samples whose innermost probe frame has only library frames beneath it, probe = helper (rs5NNN_/rs6NNN_/rs7NNN_ statics,
rs64_*{probe,tally,track,note,log,diag,stat,dump,trace,hist}*, *_probe*), control = samples under rs64_diag_spin_us /
rs64_diag_quiet_tick (inlined into rs64_store_diag_tick). CONTROL: busy-on minus busy-off control fraction >= 0.5 * busy_us * swaps/s / 1e6.
Verdict: H-free if probe share < control_delta/4 (and < 0.25 ms/frame), else H-cost with the ranked helper list.
usage: s7433_probe_cost.py DIR [--busy-us 500] [--fps 60]"""
import re, sys, os, argparse, collections
ap = argparse.ArgumentParser(); ap.add_argument('d'); ap.add_argument('--busy-us', type=float, default=500.0)
ap.add_argument('--fps', type=float, default=60.0); ap.add_argument('--top', type=int, default=25); ap.add_argument('--threads', default='[Game]', help='substring selecting the threads to attribute (e.g. "SP Task Thread")'); a = ap.parse_args()
LINE = re.compile(r'^([\s+!:|]*)(\d+) (.*)$')
WAIT = re.compile(r'mach_msg2_trap|__psynch_cvwait|semaphore_.*wait_trap|__ulock_wait|__semwait_signal|kevent|__select|'
                  r'swtch_pri|__workq_kernreturn|mach_wait_until|__psynch_mutexwait|thread_suspend|poll$|__wait4|read$|__open')
PROBE = re.compile(r'^_?(rs[2-7]\d{3}[a-z]?_\w+|rs64_s\d{3,4}\w*|rs64_\w*(probe|tally|track|note|log|diag|stat|dump|trace|hist|census|watch)\w*|\w*_probe\w*)$')
CTRL = re.compile(r'^_?(rs64_store_diag_tick|rs64_diag_spin_us|rs64_diag_quiet_tick)')
LIB = re.compile(r'printf|write|^_?_|^_platform|^mach_|pthread|std::|^clock_|mem(cpy|move|set|cmp)|^str|lock|operator|malloc|^free|dladdr|dyld|^getenv|^atoi|semaphore_signal')
SWAP = re.compile(r'^_?osViSwapBuffer_recomp')
def sym(t):
    t = t.split('  (in ')[0].strip()
    return t
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
        node = {'dep': dep, 'n': cnt, 's': sym(txt), 'kids': 0, 'path': [x['s'] for x in stack]}
        if stack: stack[-1]['kids'] += cnt
        stack.append(node); cur['nodes'].append(node)
    return threads
flips = []
for raw in open(os.path.join(a.d, 'run.tlog'), 'rb'):
    l = raw.decode('utf-8', 'replace'); ms, _, l = l.partition('\t')
    m = re.search(r'\[diag-quiet\] flip quiet=(\d) busy=(\d)', l)
    if m: flips.append((int(ms) / 1000.0, int(m[2])))
tasks = [int(m[1]) for m in re.finditer(r'\[g1e-split\] phase=\d+ .*?tasks=(\d+)', open(os.path.join(a.d, 'run.tlog'), errors='replace').read())]
fps = (sorted(tasks)[len(tasks)//2] if tasks else a.fps) or a.fps
def busy_at(t):
    b = 0
    for ft, fb in flips:
        if ft <= t: b = fb
    return b
rows = []; agg = {0: collections.Counter(), 1: collections.Counter()}; probes = {0: collections.Counter(), 1: collections.Counter()}
for ln in open(os.path.join(a.d, 'samples.idx')):
    i, st, w = ln.split(); st = float(st); w = float(w); fn = os.path.join(a.d, 'sample_%s.txt' % i)
    if not os.path.exists(fn): continue
    b0, b1 = busy_at(st + 0.5), busy_at(st + w + 1.5)   # sample(1) symbolication tail ~1 s
    straddle = b0 != b1
    th = parse(fn); g = [t for t in th if a.threads in t['name']]
    tot = run = pr = ct = sw = 0; selfc = collections.Counter(); prc = collections.Counter()
    for t in g:
        tot += t['n']
        for n in t['nodes']:
            sf = n['n'] - n['kids']
            if sf <= 0 or WAIT.search(n['s']): continue
            run += sf; selfc[n['s']] += sf
            path = n['path'] + [n['s']]
            ix = [k for k, p in enumerate(path) if PROBE.match(p)]
            # charge a probe only for its own frames + library calls beneath it; a probe WRAPPER (rs5908_call) that calls
            # game code is not charged for the game work below it
            if ix and all(LIB.search(p) or PROBE.match(p) for p in path[ix[-1] + 1:]): pr += sf; prc[path[ix[-1]]] += sf
            if any(CTRL.match(p) for p in path): ct += sf
            elif any(SWAP.match(p) for p in path): sw += sf
    rows.append((i, st, b0, straddle, len(g), tot, run, pr, ct, sw))
    if not straddle:
        agg[b0] += selfc; probes[b0] += prc
print('fps(g1e tasks/s median)=%s flips=%d' % (fps, len(flips)))
print('win start_s busy straddle guest_thr samples running probe ctrl | running_ms/frame probe_ms/frame ctrl_ms/frame')
S = {0: [0, 0, 0, 0], 1: [0, 0, 0, 0]}
for i, st, b, sd, ng, tot, run, pr, ct, sw in rows:
    per = tot / max(ng, 1)  # samples per thread ~ ms of wall
    f = lambda x: x / max(per, 1) * 1000.0 / fps
    print('%s %.1f %d %d %d %d %d %d %d | %.3f %.4f %.4f swap_other %.4f' % (i, st, b, sd, ng, tot, run, pr, ct, f(run), f(pr), f(ct), f(sw)))
    if not sd:
        s = S[b]; s[0] += per; s[1] += run; s[2] += pr; s[3] += ct
ok = S[0][0] > 0 and S[1][0] > 0
if not ok: print('VERDICT unevaluable: need busy-on and busy-off windows'); sys.exit(3)
m = {b: [S[b][k] / S[b][0] * 1000.0 / fps for k in (1, 2, 3)] for b in (0, 1)}
exp = a.busy_us / 1000.0
cd = m[1][2] - m[0][2]
print('busy=0: running %.3f probe %.4f ctrl %.4f ms/frame; busy=1: running %.3f probe %.4f ctrl %.4f ms/frame' % (*m[0], *m[1]))
print('CONTROL ctrl delta %.4f ms/frame vs expected %.3f (busy_us per swap): %s; running delta %.3f' % (cd, exp, 'PASS' if cd >= 0.5 * exp else 'FAIL', m[1][0] - m[0][0]))
print('top guest self (busy=0):'); 
for k, v in agg[0].most_common(a.top): print('  %7d %5.2f%% %s' % (v, 100.0 * v / max(sum(agg[0].values()), 1), k))
print('probe helpers (busy=0, innermost probe frame):')
for k, v in probes[0].most_common(a.top): print('  %7d %s' % (v, k))
if cd < 0.5 * exp: print('VERDICT control-fail'); sys.exit(3)
pm = m[0][1]
v = 'H-free' if pm < cd / 4 and pm < 0.25 else 'H-cost'
print('VERDICT %s probe %.4f ms/frame (control delta %.4f, threshold min(%.4f, 0.25))' % (v, pm, cd, cd / 4)); sys.exit(0 if v == 'H-free' else 1)
