#!/usr/bin/env python3
"""s7442 class CY census: every guest-side probe helper (rsNNNN_* name) that a tools/apply_s*.py patch inserted into
N64Recomp/RecompiledFuncs/funcs_*.c, classified by how its CALL SITES are gated:
  GATED         every call line is under an if/latch/__builtin_expect on the same line
  GATED-INSIDE  callee body returns on an env/flag latch within its first lines (cheap out-of-line call)
  UNGATED       neither: the helper's body runs on every call
plus, with --samples DIR (a tools/s7433_probe_cost.sh capture), the sample-weighted self/inclusive ms/frame of every rsNNNN
frame so the ranking is by real cost. UNGATED rows still need a human read: a helper that IS behaviour (a guard, a fix,
the renamed body of a hooked guest function) is UNGATED-NEEDED, not a defect.
usage: s7442_probe_gate_census.py [--funcs DIR] [--samples DIR] [--fps 60] [--all]   (exit 0)"""
import re, os, sys, glob, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rs64_zopen import zopen  # s7803: retained sample_N.txt are .zst
ap = argparse.ArgumentParser()
ap.add_argument('--funcs', default='/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs')
ap.add_argument('--samples', default=''); ap.add_argument('--fps', type=float, default=60.0)
ap.add_argument('--all', action='store_true', help='print GATED rows too')
a = ap.parse_args()
NAME = r'rs[0-9]{3,4}[a-z]?_[A-Za-z0-9_]+'
DEF = re.compile(r'^(?:static\s+)?(?:inline\s+)?[A-Za-z_][A-Za-z0-9_ \*]*?[ \*](' + NAME + r')\s*\(([^;{]*)\)\s*\{')
CALL = re.compile(r'(?<![A-Za-z0-9_])(' + NAME + r')\s*\(')
GATE_LINE = re.compile(r'\bif\s*\(|__builtin_expect|\?\s*' + NAME + r'|&&\s*' + NAME)
LATCH = re.compile(r'getenv|_en\b|_on\b|_enabled\s*\(|g_rs64_|\benabled\b|\bon\b\s*[<=!)]|\bif\s*\(\s*!\s*[A-Za-z0-9_]+\s*\)\s*return')
TOP = re.compile(r'^[A-Za-z_][^;=]*\)\s*\{');
defs = {}; calls = collections.defaultdict(list)
for fn in sorted(glob.glob(os.path.join(a.funcs, 'funcs_*.c'))):
    L = open(fn, errors='replace').read().split('\n'); cur = None
    for i, ln in enumerate(L):
        if TOP.match(ln): cur = ln
        m = DEF.match(ln)
        if m:
            body = ' '.join(L[i:i + 4])
            # body-level latch: an early return keyed on a flag/getenv within the first lines
            early = bool(re.search(r'return', body) and LATCH.search(body))
            defs.setdefault(m[1], (os.path.basename(fn), i + 1, early, ln.strip()[:90]))
            continue
        if cur is not None and re.match(r'^(?:static\s+)?[^(]*[ *]' + NAME + r'\s*\(', cur): continue  # inside a helper
        if 'PATCH' not in ln and not CALL.search(ln): continue
        for c in CALL.finditer(ln):
            pre = ln[:c.start()]
            if re.search(r'(?:void|int|unsigned|uint32_t|float|double|static|extern)\s*\**\s*$', pre): continue  # prototype
            calls[c[1]].append((os.path.basename(fn), i + 1, bool(GATE_LINE.search(pre)), ln.strip()[:110]))
cost = {}
if a.samples:
    LINE = re.compile(r'^([\s+!:|]*)(\d+) (.*)$'); RS = re.compile(r'^_?(' + NAME + r')\b')
    nwin = 0; sc = collections.Counter(); ic = collections.Counter()
    _g = {}  # s7803: plain or .zst per window (the raw-only glob read windows=0 on every retained capture)
    for f in glob.glob(os.path.join(a.samples, 'sample_*.txt')) + glob.glob(os.path.join(a.samples, 'sample_*.txt.zst')):
        _g.setdefault(re.sub(r'\.zst$', '', os.path.basename(f)), f)
    for fn in [_g[k] for k in sorted(_g)]:
        stack = []; nodes = []; nmax = 0; s1 = collections.Counter(); i1 = collections.Counter()
        for raw in zopen(fn):
            if raw.startswith('Total number in stack'): break
            m = LINE.match(raw.rstrip('\n'))
            if not m: continue
            dep, cnt, txt = len(m[1]), int(m[2]), m[3]
            if txt.startswith('Thread_'): stack = []; nmax = max(nmax, cnt); continue
            while stack and stack[-1]['dep'] >= dep: stack.pop()
            r = RS.match(txt.strip()); node = {'dep': dep, 'n': cnt, 'kids': 0, 'r': r[1] if r else None,
                                               'path': [x['r'] for x in stack if x['r']]}
            if stack: stack[-1]['kids'] += cnt
            stack.append(node); nodes.append(node)
        for n in nodes:
            sf = n['n'] - n['kids']
            if sf <= 0: continue
            if n['r']: s1[n['r']] += sf
            for f in set(n['path'] + ([n['r']] if n['r'] else [])): i1[f] += sf
        if not nmax: continue
        nwin += 1
        for k, v in s1.items(): sc[k] += v / nmax
        for k, v in i1.items(): ic[k] += v / nmax
    mf = lambda v: v * 1000.0 / a.fps / max(nwin, 1)
    cost = {k: (mf(sc[k]), mf(ic[k])) for k in ic}
    print('samples: %s windows=%d' % (a.samples, nwin))
tally = collections.Counter(); rows = []
for name in sorted(set(calls) | set(cost)):
    cs = [c for c in calls.get(name, []) if True]
    d = defs.get(name)
    if not cs and name not in cost: continue
    if cs and all(c[2] for c in cs): cls = 'GATED'
    elif d and d[2]: cls = 'GATED-INSIDE'
    elif not d: cls = 'NO-DEF'
    else: cls = 'UNGATED'
    tally[cls] += 1
    s, i = cost.get(name, (0.0, 0.0))
    rows.append((-i, cls, name, len(cs), sum(1 for c in cs if not c[2]), s, i, d))
print('%-13s %-28s %5s %5s %7s %7s  %s' % ('class', 'helper', 'calls', 'ungat', 'self', 'incl', 'defined'))
for _, cls, name, nc, nu, s, i, d in sorted(rows):
    if cls == 'GATED' and not a.all and i < 0.001: continue
    print('%-13s %-28s %5d %5d %7.3f %7.3f  %s' % (cls, name[:28], nc, nu, s, i, ('%s:%d' % d[:2]) if d else '-'))
print('totals: ' + ' '.join('%s=%d' % kv for kv in sorted(tally.items())))
