#!/usr/bin/env python3
"""s7434 class CQ analyzer: Gfx Thread host-glue decomposition from /usr/bin/sample call trees (s7433 captures).
Per sample file: running self samples of threads matching --threads (non-wait leaves), charged to the INNERMOST owned
frame (library frames beneath it are charged to it). Owner classes: ucode (factor5_ucode_*), rt64 (RT64::/rt64/
plume/Metal/MTL/AGX/IOGPU), ours (rs64_*/rsp_*/dpc*/recomp/librecomp/ultramodern), lib (nothing owned above).
Also: inclusive running ms/frame per child of rs64_run_lle_gfx and of rs64_dpc_defer_end_impl, and the immediate
owned caller of every _platform_memmove/memcpy sample.
Verdict (NEXT s7434): H-copy if memmove total >= 0.5 ms/frame with one owned caller carrying >= 0.5, H-walk if the
ours share under defer_end+record_submit >= 0.5 ms/frame, else H-rt64.
usage: s7434_gfx_glue.py sample_4.txt [sample_8.txt ...] [--threads 'Gfx Thread'] [--fps 60]"""
import re, sys, argparse, collections
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from rs64_zopen import zopen  # s7724: retained sample_*.txt.zst
ap = argparse.ArgumentParser(); ap.add_argument('files', nargs='+'); ap.add_argument('--threads', default='Gfx Thread')
ap.add_argument('--fps', type=float, default=60.0); ap.add_argument('--top', type=int, default=15); a = ap.parse_args()
LINE = re.compile(r'^([\s+!:|]*)(\d+) (.*)$')
WAIT = re.compile(r'mach_msg2_trap|__psynch_cvwait|semaphore_.*wait_trap|__ulock_wait|__semwait_signal|kevent|__select|'
                  r'swtch_pri|__workq_kernreturn|mach_wait_until|__psynch_mutexwait|thread_suspend|poll$|__wait4|read$|__open')
LIB = re.compile(r'^\?\?\?|printf|^_?_|^_platform|^mach_|pthread|^std::|^clock_|mem(cpy|move|set|cmp)|^str|lock|operator|malloc|^free|'
                 r'dladdr|dyld|^getenv|^atoi|semaphore_signal|^objc_|^xzm|^nanov2|^szone|^DYLD|^start|^thread_start')
UCODE = re.compile(r'factor5_ucode|^rs64_ucode')
RT64 = re.compile(r'RT64::|^rt64|plume|^MTL|Metal|AGX|IOGPU|IOAccel|^-\[|^MTL|hlslpp|xxh|XXH|TMEMHasher|interop::')
def sym(t): return t.split('  (in ')[0].strip()
def cls(s):
    if UCODE.search(s): return 'ucode'
    if RT64.search(s): return 'rt64'
    if LIB.search(s): return None
    return 'ours'
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
T = {k: collections.Counter() for k in ('cls', 'own', 'lle', 'defer', 'mm', 'mmsz', 'rec', 'submit')}
per_tot = 0; run_tot = 0
for fn in a.files:
    g = [t for t in parse(fn) if a.threads in t['name']]
    for t in g:
        per_tot += t['n']
        for n in t['nodes']:
            sf = n['n'] - n['kids']
            if sf <= 0 or WAIT.search(n['s']): continue
            run_tot += sf; path = n['path'] + [n['s']]
            owned = [(k, cls(p)) for k, p in enumerate(path) if cls(p)]
            c, who = (owned[-1][1], path[owned[-1][0]]) if owned else ('lib', n['s'])
            T['cls'][c] += sf; T['own'][(c, who)] += sf
            for key, anchor in (('lle', 'rs64_run_lle_gfx'), ('defer', 'rs64_dpc_defer_end_impl')):
                ix = [k for k, p in enumerate(path) if p.startswith(anchor)]
                if ix:
                    k = ix[-1]; child = path[k + 1] if k + 1 < len(path) else '(self)'
                    T[key][re.sub(r'\(.*', '', child)] += sf
                    if key == 'defer': T['defer'][('CLS', c)] += sf
            if any(p.startswith('rs64_dpc_record_submit') for p in path): T['rec'][c] += sf
            if any(p.startswith('rsp_dpc_submit_impl') for p in path): T['submit'][c] += sf
            if re.search(r'mem(move|cpy)', n['s']):
                cal = [p for p in path[:-1] if cls(p)]
                T['mm'][re.sub(r'\(.*', '', cal[-1]) if cal else '?'] += sf
n_thr = max(1, len([1]))
f = lambda x: x / max(per_tot, 1) * 1000.0 * 1000.0 / a.fps / 1000.0  # samples/total_samples * (1000 ms/s / fps)
print('files=%d thread=%r total_samples=%d running=%d -> running %.3f ms/frame' % (len(a.files), a.threads, per_tot, run_tot, f(run_tot)))
print('owner class (innermost owned frame, lib beneath charged to it):')
for k, v in T['cls'].most_common(): print('  %-6s %6d %.3f ms/frame' % (k, v, f(v)))
print('top owned frames:')
for (c, w), v in T['own'].most_common(a.top): print('  %6d %.3f %-5s %s' % (v, f(v), c, w[:110]))
print('children of rs64_run_lle_gfx (inclusive running):')
for k, v in T['lle'].most_common(a.top): print('  %6d %.3f %s' % (v, f(v), k[:110]))
print('children of rs64_dpc_defer_end_impl (inclusive running):')
for k, v in T['defer'].most_common(a.top + 5):
    if not isinstance(k, tuple): print('  %6d %.3f %s' % (v, f(v), k[:110]))
print('defer_end by owner class:', {k[1]: round(f(v), 3) for k, v in T['defer'].items() if isinstance(k, tuple)})
print('record_submit by owner class:', {k: round(f(v), 3) for k, v in T['rec'].items()})
print('rsp_dpc_submit_impl by owner class:', {k: round(f(v), 3) for k, v in T['submit'].items()})
print('memmove/memcpy self by owned caller:')
for k, v in T['mm'].most_common(a.top): print('  %6d %.3f %s' % (v, f(v), k[:110]))
mm = sum(T['mm'].values()); top = T['mm'].most_common(1)[0][1] if T['mm'] else 0
walk = sum(v for k, v in T['defer'].items() if k == ('CLS', 'ours')) + T['rec']['ours']
if f(mm) >= 0.5 and f(top) >= 0.5: v = 'H-copy'
elif f(walk) >= 0.5: v = 'H-walk'
else: v = 'H-rt64'
print('VERDICT %s memmove %.3f (top caller %.3f) ours-walk(defer_end+record_submit) %.3f ms/frame' % (v, f(mm), f(top), f(walk)))
